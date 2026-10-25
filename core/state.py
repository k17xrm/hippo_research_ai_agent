"""State for a single research session."""

from uuid import uuid4

from pydantic import BaseModel, Field

from core.events import AgentStatus
from schemas.research import ResearchPlan


class ResearchState(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    user_query: str
    research_plan: ResearchPlan | None = None
    current_status: AgentStatus = AgentStatus.WAITING
    error_message: str | None = None
