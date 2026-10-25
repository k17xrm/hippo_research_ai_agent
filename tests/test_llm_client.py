import pytest

from config.settings import Settings
from llm.client import LLMError, MockLLMClient, OpenAILLMClient, create_llm_client


def test_missing_api_key_has_actionable_error() -> None:
    with pytest.raises(LLMError, match="OPENAI_API_KEY"):
        OpenAILLMClient(Settings(openai_api_key=None))


def test_mock_mode_needs_no_api_key() -> None:
    assert isinstance(create_llm_client(Settings(openai_api_key=None), mock=True), MockLLMClient)
