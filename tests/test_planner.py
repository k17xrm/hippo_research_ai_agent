import pytest

from agents.planner import PlannerAgent, PlannerError
from core.events import AgentEvent, AgentStatus
from core.state import ResearchState
from llm.client import LLMClient, MockLLMClient


@pytest.mark.asyncio
async def test_mock_planner_runs_and_updates_state() -> None:
    state = ResearchState(user_query="Vision Transformer trends")
    plan = await PlannerAgent(MockLLMClient()).run(state.user_query, state)
    assert len(plan.tasks) == 4
    assert state.research_plan == plan
    assert state.current_status == AgentStatus.COMPLETED


@pytest.mark.asyncio
async def test_planner_emits_real_lifecycle_events() -> None:
    events: list[AgentEvent] = []
    state = ResearchState(user_query="연구 주제")
    await PlannerAgent(MockLLMClient(), events.append).run(state.user_query, state)
    assert events[0].status == AgentStatus.THINKING
    assert events[-1].status == AgentStatus.COMPLETED
    assert any(event.message == "LLM response received." for event in events)
    assert any(event.message == "ResearchPlan validated." for event in events)


class InvalidLLM(LLMClient):
    async def generate_plan(self, query: str, system_prompt: str) -> dict:
        return {"original_query": query, "research_goal": "goal", "tasks": []}


@pytest.mark.asyncio
async def test_invalid_llm_output_sets_error_state() -> None:
    state = ResearchState(user_query="topic")
    with pytest.raises(PlannerError, match="invalid"):
        await PlannerAgent(InvalidLLM()).run(state.user_query, state)
    assert state.current_status == AgentStatus.ERROR
    assert state.error_message is not None
