from io import StringIO

import pytest
from rich.console import Console

from ui.cli import run_cli


@pytest.mark.asyncio
async def test_cli_mock_query() -> None:
    output = StringIO()
    console = Console(file=output, force_terminal=False, width=100)
    exit_code = await run_cli(mock=True, query="Robotics research", console=console)
    assert exit_code == 0
    assert "MODE: DEMO" in output.getvalue()
    assert "RESEARCH DECOMPOSITION" in output.getvalue()
