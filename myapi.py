from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Optional

from huggingface_hub import InferenceClient


class APIError(RuntimeError):
    """User-safe API error for UI display."""


def _load_hf_token() -> Optional[str]:
    # Prefer env vars for deployments (Streamlit Cloud, Docker, CI, etc.)
    token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if token:
        return token.strip() or None

    # Optional local development fallback: `secret.py` with `HF_TOKEN = "..."`.
    # This file must be gitignored and never committed.
    try:
        import importlib

        secret = importlib.import_module("secret")
        value = getattr(secret, "HF_TOKEN", None)
        if isinstance(value, str) and value.strip():
            return value.strip()
    except Exception:
        return None

    return None


@dataclass(frozen=True)
class EmotionResult:
    emotion: str
    confidence: float


class API:
    NER_MODEL = "dslim/bert-base-NER"
    EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"

    def __init__(self, token: Optional[str] = None):
        self._token = (token or _load_hf_token() or "").strip() or None
        self._client: Optional[InferenceClient] = None

    def _get_client(self) -> InferenceClient:
        if not self._token:
            raise APIError(
                "Missing Hugging Face token. Set env var HF_TOKEN (recommended) "
                "or create a local secret.py with HF_TOKEN, but never commit it."
            )
        if self._client is None:
            # Correct usage for deployment: InferenceClient(api_key=HF_TOKEN)
            self._client = InferenceClient(api_key=self._token)
        return self._client

    def _wrap_hf_exception(self, feature: str, e: Exception) -> APIError:
        msg = str(e) or e.__class__.__name__
        lower = msg.lower()
        if "401" in lower or "unauthorized" in lower or "invalid username or password" in lower:
            return APIError(
                "Hugging Face authorization failed (401). "
                "On Streamlit Cloud, set app Secrets: HF_TOKEN=\"hf_...\". "
                "Locally, set environment variable HF_TOKEN. "
                "Also ensure the token is valid and has permission to use inference."
            )
        return APIError(f"Hugging Face {feature} request failed: {msg}")

    def perform_ner(self, text: str) -> str:
        text = (text or "").strip()
        if not text:
            raise APIError("Please enter some text for Named Entity Recognition.")

        try:
            result = self._get_client().token_classification(text, model=self.NER_MODEL)
        except Exception as e:
            raise self._wrap_hf_exception("NER", e) from e

        if not result:
            return "No entities detected."

        entities: list[str] = []
        for item in result if isinstance(result, list) else []:
            if not isinstance(item, dict):
                continue
            word = item.get("word") or item.get("entity") or ""
            group = item.get("entity_group") or item.get("entity") or ""
            word = str(word).strip()
            group = str(group).strip()
            if word and group:
                entities.append(f"{word} : {group}")
            elif word:
                entities.append(word)

        return "\n".join(entities) if entities else "No entities detected."

    def perform_emotion_detection(self, text: str) -> dict[str, Any]:
        text = (text or "").strip()
        if not text:
            raise APIError("Please enter some text for Emotion Detection.")

        try:
            result = self._get_client().text_classification(text, model=self.EMOTION_MODEL)
        except Exception as e:
            raise self._wrap_hf_exception("emotion", e) from e

        top = None
        if isinstance(result, list) and result:
            top = result[0]

        if not isinstance(top, dict):
            return {"emotion": "unknown", "confidence": 0.0}

        label = top.get("label")
        score = top.get("score")

        emotion = str(label).strip() if isinstance(label, str) and label.strip() else "unknown"
        try:
            confidence = float(score) if score is not None else 0.0
        except (TypeError, ValueError):
            confidence = 0.0

        return {"emotion": emotion, "confidence": round(confidence, 2)}
