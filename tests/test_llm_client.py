from config.settings import Settings
from llm.client import (
    MockLLMClient,
    OllamaLLMClient,
    _parse_research_plan_response,
    create_llm_client,
)


def test_ollama_provider_creates_ollama_client() -> None:
    client = create_llm_client(Settings(llm_provider="ollama"))
    assert isinstance(client, OllamaLLMClient)


def test_mock_mode_uses_mock_client() -> None:
    assert isinstance(create_llm_client(Settings(), mock=True), MockLLMClient)


def test_qwen_nested_plan_response_is_normalized() -> None:
    raw_response = """
    {
      "research_plan": {
        "title": "Robotics trends",
        "objective": "Analyze current robotics research trends.",
        "tasks": [
          {"id": "task-1", "title": "Scope", "objective": "Define the scope."},
          {"id": "task-2", "title": "Methods", "objectives": "Compare methods."},
          {"id": "task-3", "title": "Future work", "objective": "Identify open problems."}
        ]
      }
    }
    """

    plan = _parse_research_plan_response(raw_response, "Robotics trends")

    assert plan.original_query == "Robotics trends"
    assert plan.research_goal == "Analyze current robotics research trends."
    assert plan.tasks[1].objective == "Compare methods."
