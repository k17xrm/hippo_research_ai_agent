"""Planner agent: research decomposition only, no paper retrieval."""

from pathlib import Path
from typing import Any

from pydantic import ValidationError

from agents.base import BaseAgent
from core.events import AgentStatus, EventHandler
from core.state import ResearchState
from llm.client import LLMClient, LLMError
from schemas.research import ResearchPlan


class PlannerError(RuntimeError):
    pass


class PlannerAgent(BaseAgent):
    name = "planner"

    def __init__(
        self,
        llm_client: LLMClient,
        event_handler: EventHandler | None = None,
        prompt_path: Path | None = None,
    ) -> None:
        super().__init__(event_handler)
        self.llm_client = llm_client
        self.prompt_path = prompt_path or (
            Path(__file__).resolve().parents[1] / "prompts" / "planner.md"
        )

    async def run(self, query: str, state: ResearchState) -> ResearchPlan:
        query = query.strip()
        if not query:
            await self._fail(state, "Research topic must not be empty.")
            raise PlannerError("Research topic must not be empty.")

        try:
            state.current_status = AgentStatus.THINKING
            await self.emit(AgentStatus.THINKING, "Understanding research topic...")
            prompt = self.prompt_path.read_text(encoding="utf-8")

            state.current_status = AgentStatus.WORKING
            await self.emit(AgentStatus.WORKING, "Requesting LLM research plan...")
            raw_plan: Any = await self.llm_client.generate_plan(query, prompt)
            await self.emit(AgentStatus.WORKING, "LLM response received.")
            await self.emit(AgentStatus.WORKING, "Validating ResearchPlan...")

            plan = (
                raw_plan
                if isinstance(raw_plan, ResearchPlan)
                else ResearchPlan.model_validate_json(raw_plan)
                if isinstance(raw_plan, (str, bytes, bytearray))
                else ResearchPlan.model_validate(raw_plan)
            )
            state.research_plan = plan
            state.current_status = AgentStatus.COMPLETED
            state.error_message = None
            await self.emit(AgentStatus.WORKING, "ResearchPlan validated.")
            await self.emit(AgentStatus.COMPLETED, "Planner completed.")
            return plan
        except (ValidationError, ValueError, TypeError) as exc:
            await self._fail(state, "The LLM returned an invalid research plan.")
            raise PlannerError("The LLM returned an invalid research plan.") from exc
        except (LLMError, OSError) as exc:
            await self._fail(state, str(exc))
            raise PlannerError(str(exc)) from exc

    async def _fail(self, state: ResearchState, message: str) -> None:
        state.current_status = AgentStatus.ERROR
        state.error_message = message
        await self.emit(AgentStatus.ERROR, message)
