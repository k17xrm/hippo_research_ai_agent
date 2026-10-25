"""Environment-backed application settings."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class Settings:
    llm_provider: str = "ollama"
    llm_model: str = "qwen3:8b"
    llm_timeout: float = 120.0
    ollama_host: str = "http://127.0.0.1:11434"

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        return cls(
            llm_provider=os.getenv("LLM_PROVIDER", "ollama").lower(),
            llm_model=os.getenv("LLM_MODEL", "qwen3:8b"),
            llm_timeout=float(os.getenv("LLM_TIMEOUT", "120")),
            ollama_host=os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434"),
        )
