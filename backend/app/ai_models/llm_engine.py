"""
LLM Engine — configurable language model for enhanced explanations.
Supports: "none" (template-based), "local" (Ollama), "external" (custom API).
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class LLMEngine:
    """Configurable LLM for explanation enhancement."""

    def __init__(self, provider: str = "none", model: str = "tinyllama",
                 base_url: str = "http://localhost:11434",
                 api_key: Optional[str] = None, external_model: Optional[str] = None):
        self.provider = provider
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.external_model = external_model
        self._available: Optional[bool] = None

    @property
    def is_available(self) -> bool:
        if self.provider == "none":
            return True  # template-based always available
        if self._available is None:
            self._available = self._check_availability()
        return self._available

    def _check_availability(self) -> bool:
        if self.provider == "local":
            try:
                import httpx
                r = httpx.get(f"{self.base_url}/api/version", timeout=3)
                return r.status_code == 200
            except Exception:
                logger.warning("Ollama not reachable. LLM enhancement unavailable.")
                return False
        if self.provider == "external":
            return bool(self.api_key)
        return True

    def enhance(self, raw_explanation: str, context: dict, mode: str) -> str:
        """Optionally enhance the explanation using an LLM."""
        if self.provider == "none" or not self.is_available:
            return raw_explanation  # pass-through

        if self.provider == "local":
            return self._call_ollama(raw_explanation, mode)
        elif self.provider == "external":
            return self._call_external(raw_explanation, mode)

        return raw_explanation

    def _call_ollama(self, text: str, mode: str) -> str:
        try:
            import httpx
            system = self._system_prompt(mode)
            payload = {
                "model": self.model,
                "prompt": f"{system}\n\nContent to improve:\n{text}",
                "stream": False,
            }
            r = httpx.post(f"{self.base_url}/api/generate", json=payload, timeout=60)
            if r.status_code == 200:
                return r.json().get("response", text)
        except Exception as e:
            logger.warning(f"Ollama call failed: {e}")
        return text

    def _call_external(self, text: str, mode: str) -> str:
        try:
            import httpx
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {
                "model": self.external_model or "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": self._system_prompt(mode)},
                    {"role": "user", "content": text},
                ],
                "max_tokens": 500,
            }
            r = httpx.post(
                f"{self.base_url}/chat/completions",
                json=payload, headers=headers, timeout=30
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"External LLM call failed: {e}")
        return text

    def _system_prompt(self, mode: str) -> str:
        base = ("You are an accessibility assistant helping visually impaired students "
                "understand visual content. Never invent information not present. "
                "Be clear, concise, and helpful.")
        if mode == "explain":
            return base + " Explain the content in simple, easy-to-understand language."
        elif mode == "summarize":
            return base + " Provide a brief, structured summary of the key points only."
        else:
            return base + " Faithfully narrate all detected content."
