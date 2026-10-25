import pytest

from core.events import AgentStatus
from core.orchestrator import ResearchOrchestrator
from llm.client import MockLLMClient


@pytest.mark.asyncio
async def test_orchestrator_runs_planner() -> None:
    state = await ResearchOrchestrator(MockLLMClient()).run("Battery recycling")
    assert state.current_status == AgentStatus.COMPLETED
    assert state.research_plan is not None
    assert state.research_plan.original_query == "Battery recycling"
