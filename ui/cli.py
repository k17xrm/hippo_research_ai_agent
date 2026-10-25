"""Rich command-line interface."""

import asyncio

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from agents.planner import PlannerError
from config.settings import Settings
from core.events import AgentEvent
from core.orchestrator import ResearchOrchestrator
from llm.client import LLMError, create_llm_client
from schemas.research import ResearchPlan


def render_plan(console: Console, plan: ResearchPlan) -> None:
    console.print(Panel(plan.research_goal, title="RESEARCH GOAL", border_style="magenta"))
    table = Table(title="RESEARCH DECOMPOSITION", expand=True, show_lines=True)
    table.add_column("#", width=4, style="bright_magenta")
    table.add_column("Task", style="bold")
    table.add_column("Objective")
    for index, task in enumerate(plan.tasks, start=1):
        table.add_row(f"{index:02d}", task.title, task.objective)
    console.print(table)
    console.print("[dim]Planning output only; no literature search has been performed.[/dim]")


async def run_cli(mock: bool = False, query: str | None = None, console: Console | None = None) -> int:
    console = console or Console()
    mode = "DEMO" if mock else "LIVE"
    title = Text.assemble(
        ("RESEARCH HIPPO\n", "bold bright_magenta"),
        ("AI Research Assistant\n", "bold"),
        (f"MODE: {mode}", "yellow" if mock else "green"),
    )
    console.print(Panel(Align.center(title), border_style="bright_magenta"))
    if query is None:
        query = console.input("\n[bold]Enter Research Topic:[/bold]\n> ")
    if not query.strip():
        console.print("[bold red]Error:[/bold red] Research topic must not be empty.")
        return 2

    def on_event(event: AgentEvent) -> None:
        live_status.update(f"[bright_magenta]🦛 Planner:[/bright_magenta] {event.message}")
        console.print(
            f"[bright_magenta][{event.agent.upper()}][/bright_magenta] "
            f"[bold]{event.status.value.upper()}[/bold] — {event.message}"
        )

    try:
        client = create_llm_client(Settings.from_env(), mock=mock)
        with console.status("[bright_magenta]🦛 Planner is starting...[/bright_magenta]") as live_status:
            state = await ResearchOrchestrator(client, on_event).run(query)
        assert state.research_plan is not None
        render_plan(console, state.research_plan)
        return 0
    except (LLMError, PlannerError) as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        return 1


def start_cli(mock: bool = False) -> int:
    return asyncio.run(run_cli(mock=mock))
