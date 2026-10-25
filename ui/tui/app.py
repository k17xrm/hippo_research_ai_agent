"""Responsive Textual application for the planner MVP."""

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Footer, Header, Input, Label, RichLog, Static

from agents.planner import PlannerError
from config.settings import Settings
from core.events import AgentEvent
from core.orchestrator import ResearchOrchestrator
from llm.client import LLMError, create_llm_client
from ui.tui.widgets import AgentCard


class ResearchHippoApp(App[None]):
    CSS_PATH = "theme.tcss"
    TITLE = "Research Hippo"
    SUB_TITLE = "Multi-Agent Research Assistant"

    def __init__(self, mock: bool = False) -> None:
        super().__init__()
        self.mock = mock

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(f"MODE: {'DEMO' if self.mock else 'LIVE'}", id="mode")
        yield Label("RESEARCH TOPIC", classes="section-title")
        yield Input(placeholder="Enter a research topic and press Enter", id="topic")
        yield Label("AGENT WORKSPACE", classes="section-title")
        yield AgentCard(id="planner-card")
        yield Label("RESEARCH DECOMPOSITION", classes="section-title")
        with VerticalScroll(id="results"):
            yield Static("Submit a topic to generate a research plan.", id="result-content")
        yield Label("ACTIVITY LOG", classes="section-title")
        yield RichLog(id="activity", markup=True, max_lines=100)
        yield Footer()

    @on(Input.Submitted, "#topic")
    def submit_topic(self, event: Input.Submitted) -> None:
        query = event.value.strip()
        if not query:
            self.query_one("#activity", RichLog).write("[red]Research topic must not be empty.[/red]")
            return
        event.input.disabled = True
        self.run_research(query)

    def receive_event(self, event: AgentEvent) -> None:
        self.call_from_thread(self._apply_event, event)

    def _apply_event(self, event: AgentEvent) -> None:
        self.query_one(AgentCard).show_event(event)
        time = event.timestamp.astimezone().strftime("%H:%M:%S")
        self.query_one("#activity", RichLog).write(
            f"[dim]{time}[/dim] [bright_magenta][{event.agent.title()}][/bright_magenta] {event.message}"
        )

    @work(thread=True, exclusive=True, group="research")
    def run_research(self, query: str) -> None:
        import asyncio

        try:
            client = create_llm_client(Settings.from_env(), mock=self.mock)
            state = asyncio.run(ResearchOrchestrator(client, self.receive_event).run(query))
            assert state.research_plan is not None
            lines = [f"[bold magenta]GOAL[/bold magenta]\n{state.research_plan.research_goal}\n"]
            for index, task in enumerate(state.research_plan.tasks, start=1):
                lines.append(f"[bold]{index:02d}. {task.title}[/bold]\n    {task.objective}")
            lines.append("\n[dim]Planning output only; no literature search has been performed.[/dim]")
            self.call_from_thread(
                self.query_one("#result-content", Static).update, "\n\n".join(lines)
            )
        except (LLMError, PlannerError) as exc:
            self.call_from_thread(
                self.query_one("#activity", RichLog).write, f"[bold red]Error: {exc}[/bold red]"
            )
        finally:
            self.call_from_thread(setattr, self.query_one("#topic", Input), "disabled", False)


def start_tui(mock: bool = False) -> None:
    ResearchHippoApp(mock=mock).run()
