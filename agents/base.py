"""Minimal common interface for present and future agents."""

import inspect
from abc import ABC, abstractmethod
from typing import Any

from core.events import AgentEvent, AgentStatus, EventHandler


class BaseAgent(ABC):
    name: str

    def __init__(self, event_handler: EventHandler | None = None) -> None:
        self.event_handler = event_handler

    async def emit(self, status: AgentStatus, message: str) -> None:
        if self.event_handler is None:
            return
        result = self.event_handler(
            AgentEvent(agent=self.name, status=status, message=message)
        )
        if inspect.isawaitable(result):
            await result

    @abstractmethod
    async def run(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError
