"""Speech-to-text with NCAIR's N-ATLaS ASR models (Whisper-small fine-tunes).

One model per language, downloaded and loaded on first use:

    en -> NCAIR1/NigerianAccentedEnglish
    ha -> NCAIR1/Hausa-ASR
    ig -> NCAIR1/Igbo-ASR
    yo -> NCAIR1/Yoruba-ASR

The models are gated: accept their terms on Hugging Face, then `hf auth login`.
A pre-downloaded copy in NATLAS_ASR_DIR/<lang>/ (default server/models/asr) is used
first. They run on the CPU by default so the GPU stays free for the chat model
(NATLAS_ASR_DEVICE=cuda to change). Extra dependencies: requirements-speech.txt.
"""

from __future__ import annotations

import io
import os
import threading
from math import gcd
from pathlib import Path

ASR_MODELS = {
    "en": "NCAIR1/NigerianAccentedEnglish",
    "ha": "NCAIR1/Hausa-ASR",
    "ig": "NCAIR1/Igbo-ASR",
    "yo": "NCAIR1/Yoruba-ASR",
}
SAMPLE_RATE = 16000
MAX_AUDIO_BYTES = 25 * 1024 * 1024  # same limit as OpenAI's transcription API
# Weights and tokenizer only; the repos also hold optimizer and trainer state.
_ALLOW = ["*.json", "*.txt", "pytorch_model.bin", "*.safetensors"]


class SpeechUnavailable(RuntimeError):
    """Speech dependencies missing or a model could not be downloaded."""


class AudioError(ValueError):
    """The uploaded bytes are not readable audio."""


def decode_audio(audio: bytes):
    """Any WAV/FLAC/OGG/MP3 -> mono float32 at 16 kHz."""
    try:
        import numpy as np
        import soundfile as sf
    except ImportError as e:
        raise SpeechUnavailable("Speech is not installed: pip install -r requirements-speech.txt") from e
    try:
        data, sr = sf.read(io.BytesIO(audio), dtype="float32", always_2d=True)
    except Exception as e:
        raise AudioError("Could not read the audio. Send WAV, FLAC, OGG or MP3.") from e
    data = data.mean(axis=1)
    if sr != SAMPLE_RATE:
        from scipy.signal import resample_poly
        g = gcd(sr, SAMPLE_RATE)
        data = resample_poly(data, SAMPLE_RATE // g, sr // g)
    return np.ascontiguousarray(data, dtype=np.float32)


class WhisperTranscriber:
    name = "whisper"

    def __init__(self):
        self._pipes = {}
        self._lock = threading.Lock()
        self.device = os.environ.get("NATLAS_ASR_DEVICE", "cpu")
        self.local_dir = Path(os.environ.get(
            "NATLAS_ASR_DIR", Path(__file__).resolve().parent.parent / "models" / "asr"))

    def _pipe(self, lang: str):
        with self._lock:
            if lang not in self._pipes:
                try:
                    from huggingface_hub import snapshot_download
                    from transformers import pipeline
                except ImportError as e:
                    raise SpeechUnavailable(
                        "Speech is not installed: pip install -r requirements-speech.txt") from e
                local = self.local_dir / lang
                if (local / "config.json").exists() and (local / "pytorch_model.bin").exists():
                    path = str(local)
                else:
                    try:
                        path = snapshot_download(ASR_MODELS[lang], allow_patterns=_ALLOW)
                    except Exception as e:
                        raise SpeechUnavailable(
                            f"Could not download {ASR_MODELS[lang]}. Accept its terms on Hugging "
                            "Face and run `hf auth login`.") from e
                self._pipes[lang] = pipeline("automatic-speech-recognition", model=path,
                                             device=self.device)
            return self._pipes[lang]

    def transcribe(self, audio: bytes, lang: str) -> str:
        samples = decode_audio(audio)
        if samples.size == 0:
            raise AudioError("The audio is empty.")
        pipe = self._pipe(lang)
        # Default generation, as in NCAIR's model cards; 30 s chunks (the models' context).
        out = pipe({"raw": samples, "sampling_rate": SAMPLE_RATE}, chunk_length_s=30)
        return out["text"].strip()


class MockTranscriber:
    """No model: lets tests and SDKs exercise the endpoint offline."""

    name = "mock"

    def transcribe(self, audio: bytes, lang: str) -> str:
        return f"[mock N-ATLAS ASR] {len(audio)} bytes of {lang} audio"


def load_transcriber():
    if os.environ.get("NATLAS_BACKEND", "llamacpp").lower() == "mock":
        return MockTranscriber()
    return WhisperTranscriber()
