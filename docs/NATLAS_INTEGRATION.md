# N-ATLAS Integration Evidence

This document shows exactly where and how the Dev Kit integrates with N-ATLAS. No other foundation model is used anywhere in the kit.

## 1. Model sources

| Backend | Model loaded | Code |
|---|---|---|
| `llamacpp` (default) | `tosinamuda/N-ATLaS-GGUF` → `N-ATLaS-GGUF-Q4_K_M.gguf`, a quantized build of `NCAIR1/N-ATLaS` (listed on Hugging Face as a quantization of the base model) | `server/natlas_server/backends.py` → `LlamaCppBackend` |
| `transformers` | `NCAIR1/N-ATLaS` official weights | `server/natlas_server/backends.py` → `TransformersBackend` |

Both backends can be pointed at any other N-ATLaS build with `NATLAS_GGUF_REPO`, `NATLAS_GGUF_FILE`, `NATLAS_MODEL_PATH` or `NATLAS_HF_MODEL`.

## 2. Faithful use of the model card

The `transformers` backend follows NCAIR's published usage exactly:

- `tokenizer.apply_chat_template(..., add_generation_prompt=True, date_string=...)`
- `torch_dtype=torch.float16`, `device_map="auto"`
- `repetition_penalty=1.12`, low temperature (0.1 default)
- Default system prompt from the model card ("You are a large language model trained by Awarri AI technologies...")

The `llamacpp` backend uses the Llama-3 chat format (N-ATLaS is fine-tuned from Llama-3 8B) with the same repetition penalty.

## 3. N-ATLAS-specific features

- `reply_language` parameter (`en`, `ha`, `ig`, `yo`): restricted to exactly the four languages N-ATLAS supports.
- `/v1/translate`: translation between N-ATLAS's four languages.
- `/v1/detect-language`: routes input among N-ATLAS's four languages.
- Ready-made prompts in the SDKs tuned for Nigerian use cases.

## 4. Attribution and licence compliance

- Response header on every call: `X-Powered-By: N-ATLaS (Awarri Technologies / FMCIDE)`
- `ATTRIBUTION` constant exported by both SDKs and shown in the starter app footer
- README states the N-ATLaS Terms of Use, including the 1,000 active-user cap and the permitted and prohibited use cases
- The kit itself is developer infrastructure for education and community innovation, a permitted use

## 5. Proof it runs

Attach to the submission:

- [x] **Official weights on a free Colab T4** ([screenshot](../submission/screenshots/colab-official-weights-evidence.png)): `NCAIR1/N-ATLaS` loaded in 4-bit by the `transformers` backend (`/health` → `"backend": "transformers"`, 6 GB of 15 GB GPU memory), `X-Powered-By: N-ATLaS (Awarri Technologies / FMCIDE)`, and a Hausa answer to the model card's own question (`menene ake nufi da gwagwarmaya`): 200 tokens in 19.2 s. Reproduce with [`server/natlas_colab.ipynb`](https://colab.research.google.com/github/Akindats1/natlas-devkit/blob/main/server/natlas_colab.ipynb).
- [x] **Quantised build on a laptop GPU** ([screenshot](../submission/screenshots/playground-hausa-answer.png)): the playground answering a Hausa question through the `llamacpp` backend on a 6 GB GTX 1660 Ti, first word in 0.9 s.
- [ ] The video demonstration (see `submission/VIDEO_SCRIPT.md`)
