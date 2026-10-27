"""Environment-backed application settings."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class Settings:
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    llm_timeout: float = 60.0
    ollama_host: str = "http://127.0.0.1:11434"
    openai_api_key: str | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        return cls(
            llm_provider=os.getenv("LLM_PROVIDER", "openai").lower(),
            llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            llm_timeout=float(os.getenv("LLM_TIMEOUT", "60")),
            ollama_host=os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434"),
            openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        )
