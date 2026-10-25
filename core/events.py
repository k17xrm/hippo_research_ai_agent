"""UI-neutral lifecycle events emitted by agents."""

from datetime import datetime, timezone
from enum import Enum
from typing import Awaitable, Callable, TypeAlias

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    WAITING = "waiting"
    THINKING = "thinking"
    WORKING = "working"
    COMPLETED = "completed"
    ERROR = "error"


class AgentEvent(BaseModel):
    agent: str
    status: AgentStatus
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


EventHandler: TypeAlias = Callable[[AgentEvent], None | Awaitable[None]]
