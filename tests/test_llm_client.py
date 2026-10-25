from config.settings import Settings
from llm.client import MockLLMClient, OllamaLLMClient, create_llm_client


def test_ollama_provider_creates_ollama_client() -> None:
    client = create_llm_client(Settings(llm_provider="ollama"))
    assert isinstance(client, OllamaLLMClient)


def test_mock_mode_uses_mock_client() -> None:
    assert isinstance(create_llm_client(Settings(), mock=True), MockLLMClient)
