"""Controls the MVP agent workflow."""

from agents.planner import PlannerAgent
from core.events import EventHandler
from core.state import ResearchState
from llm.client import LLMClient


class ResearchOrchestrator:
    def __init__(self, llm_client: LLMClient, event_handler: EventHandler | None = None) -> None:
        self.planner = PlannerAgent(llm_client, event_handler)
        self.state: ResearchState | None = None

    async def run(self, user_query: str) -> ResearchState:
        self.state = ResearchState(user_query=user_query.strip())
        await self.planner.run(user_query, self.state)
        return self.state
