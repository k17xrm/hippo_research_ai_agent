"""Reusable Textual widgets."""

import os

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label, LoadingIndicator, Static

from core.events import AgentEvent


class AgentCard(Vertical):
    """A UI-only view of an agent's latest public lifecycle event."""

    def compose(self) -> ComposeResult:
        icon = "(HIPPO)" if os.getenv("RESEARCH_HIPPO_ASCII") == "1" else "🦛"
        yield Label(f"{icon}  PLANNER AGENT", id="agent-name")
        yield Label("STATUS: WAITING", id="agent-status", classes="waiting")
        yield LoadingIndicator(id="agent-spinner")
        yield Static("Ready for a research topic.", id="agent-message")

    def show_event(self, event: AgentEvent) -> None:
        status = self.query_one("#agent-status", Label)
        status.update(f"STATUS: {event.status.value.upper()}")
        status.set_classes(event.status.value)
        self.query_one("#agent-spinner", LoadingIndicator).display = event.status.value in {
            "thinking",
            "working",
        }
        self.query_one("#agent-message", Static).update(event.message)
