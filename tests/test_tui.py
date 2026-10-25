import pytest
from textual.widgets import Input, Static

from ui.tui.app import ResearchHippoApp


@pytest.mark.asyncio
async def test_tui_mock_submission_completes() -> None:
    app = ResearchHippoApp(mock=True)
    async with app.run_test(size=(100, 40)) as pilot:
        topic = app.query_one("#topic", Input)
        topic.value = "Computer vision trends"
        topic.focus()
        await pilot.press("enter")
        await app.workers.wait_for_complete()
        await pilot.pause()

        result = str(app.query_one("#result-content", Static).render())
        assert "Concepts and scope" in result
        assert topic.disabled is False
