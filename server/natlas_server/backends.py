"""Model backends. Every backend exposes the same two methods:

    generate(messages, **params) -> (text, usage)
    stream(messages, **params)   -> iterator of text chunks

Backends:
  - llamacpp     : quantized GGUF (runs on a laptop CPU, ~5 GB RAM for Q4_K_M)
  - transformers : official NCAIR1/N-ATLaS weights (needs a GPU, e.g. Colab T4)
  - mock         : no model, for CI / SDK testing / offline demos
"""

from __future__ import annotations

import os
import time
from datetime import datetime
from typing import Iterator

from .prompts import DEFAULT_SYSTEM_PROMPT


def _with_system(messages: list[dict]) -> list[dict]:
    if messages and messages[0].get("role") == "system":
        return messages
    return [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT}, *messages]


class Backend:
    name = "base"

    def generate(self, messages, max_tokens=512, temperature=0.1, top_p=0.95, stop=None):
        raise NotImplementedError

    def stream(self, messages, max_tokens=512, temperature=0.1, top_p=0.95, stop=None) -> Iterator[str]:
        text, _ = self.generate(messages, max_tokens, temperature, top_p, stop)
        yield text


class MockBackend(Backend):
    """Deterministic fake model. Lets developers build & test against the
    API shape before downloading 5 GB of weights."""

    name = "mock"

    def generate(self, messages, max_tokens=512, temperature=0.1, top_p=0.95, stop=None):
        last = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        text = f"[mock N-ATLAS] You said: {last}"
        usage = {
            "prompt_tokens": sum(len(m["content"].split()) for m in messages),
            "completion_tokens": len(text.split()),
        }
        usage["total_tokens"] = usage["prompt_tokens"] + usage["completion_tokens"]
        return text, usage

    def stream(self, messages, **kw):
        text, _ = self.generate(messages, **kw)
        for word in text.split(" "):
            time.sleep(0.02)
            yield word + " "


class LlamaCppBackend(Backend):
    name = "llamacpp"

    def __init__(self):
        from llama_cpp import Llama  # pip install llama-cpp-python

        path = os.environ.get("NATLAS_MODEL_PATH")
        n_ctx = int(os.environ.get("NATLAS_CTX", "4096"))
        n_gpu = int(os.environ.get("NATLAS_GPU_LAYERS", "0"))
        if path and os.path.exists(path):
            self.llm = Llama(model_path=path, n_ctx=n_ctx, n_gpu_layers=n_gpu,
                             chat_format="llama-3", verbose=False)
        else:
            repo = os.environ.get("NATLAS_GGUF_REPO", "tosinamuda/N-ATLaS-GGUF")
            fname = os.environ.get("NATLAS_GGUF_FILE", "N-ATLaS-GGUF-Q4_K_M.gguf")
            self.llm = Llama.from_pretrained(repo_id=repo, filename=fname, n_ctx=n_ctx,
                                             n_gpu_layers=n_gpu, chat_format="llama-3",
                                             verbose=False)

    def _params(self, max_tokens, temperature, top_p, stop):
        return dict(max_tokens=max_tokens, temperature=temperature, top_p=top_p,
                    stop=stop, repeat_penalty=1.12)

    def generate(self, messages, max_tokens=512, temperature=0.1, top_p=0.95, stop=None):
        out = self.llm.create_chat_completion(messages=_with_system(messages),
                                              **self._params(max_tokens, temperature, top_p, stop))
        return out["choices"][0]["message"]["content"], out.get("usage", {})

    def stream(self, messages, max_tokens=512, temperature=0.1, top_p=0.95, stop=None):
        for chunk in self.llm.create_chat_completion(messages=_with_system(messages), stream=True,
                                                     **self._params(max_tokens, temperature, top_p, stop)):
            piece = chunk["choices"][0]["delta"].get("content")
            if piece:
                yield piece


class TransformersBackend(Backend):
    """Official weights, as in the NCAIR model card. Requires GPU + HF token
    with the model terms accepted (huggingface-cli login)."""

    name = "transformers"

    def __init__(self):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        model_id = os.environ.get("NATLAS_HF_MODEL", "NCAIR1/N-ATLaS")
        self.torch = torch
        self.tok = AutoTokenizer.from_pretrained(model_id)
        kwargs = dict(torch_dtype=torch.float16, device_map="auto")
        if os.environ.get("NATLAS_LOAD_4BIT") == "1":
            from transformers import BitsAndBytesConfig
            kwargs["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True,
                                                               bnb_4bit_compute_dtype=torch.float16)
        self.model = AutoModelForCausalLM.from_pretrained(model_id, **kwargs)

    def _encode(self, messages):
        text = self.tok.apply_chat_template(_with_system(messages), add_generation_prompt=True,
                                            tokenize=False,
                                            date_string=datetime.now().strftime("%d %b %Y"))
        return self.tok(text, return_tensors="pt", add_special_tokens=False).to(self.model.device)

    def _gen_kwargs(self, max_tokens, temperature, top_p):
        kw = dict(max_new_tokens=max_tokens, repetition_penalty=1.12, use_cache=True)
        if temperature and temperature > 0:
            kw.update(do_sample=True, temperature=temperature, top_p=top_p)
        return kw

    def generate(self, messages, max_tokens=512, temperature=0.1, top_p=0.95, stop=None):
        inputs = self._encode(messages)
        with self.torch.no_grad():
            out = self.model.generate(**inputs, **self._gen_kwargs(max_tokens, temperature, top_p))
        new = out[0][inputs["input_ids"].shape[1]:]
        text = self.tok.decode(new, skip_special_tokens=True).strip()
        p, c = inputs["input_ids"].shape[1], len(new)
        return text, {"prompt_tokens": p, "completion_tokens": c, "total_tokens": p + c}

    def stream(self, messages, max_tokens=512, temperature=0.1, top_p=0.95, stop=None):
        from threading import Thread
        from transformers import TextIteratorStreamer

        inputs = self._encode(messages)
        streamer = TextIteratorStreamer(self.tok, skip_prompt=True, skip_special_tokens=True)
        Thread(target=self.model.generate,
               kwargs=dict(**inputs, streamer=streamer,
                           **self._gen_kwargs(max_tokens, temperature, top_p))).start()
        for piece in streamer:
            if piece:
                yield piece


def load_backend() -> Backend:
    kind = os.environ.get("NATLAS_BACKEND", "llamacpp").lower()
    if kind == "mock":
        return MockBackend()
    if kind == "transformers":
        return TransformersBackend()
    if kind == "llamacpp":
        return LlamaCppBackend()
    raise ValueError(f"Unknown NATLAS_BACKEND '{kind}' (use llamacpp, transformers or mock)")
