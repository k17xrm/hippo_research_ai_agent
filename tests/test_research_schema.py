import pytest
from pydantic import ValidationError

from schemas.research import ResearchPlan, ResearchTask


def task(identifier: str = "task-1") -> ResearchTask:
    return ResearchTask(id=identifier, title="Scope", objective="Define the scope.")


def test_research_task_creation() -> None:
    assert task().title == "Scope"


def test_research_plan_creation_and_json_serialization() -> None:
    plan = ResearchPlan(original_query="A topic", research_goal="Understand it", tasks=[task(f"task-{n}") for n in range(1, 4)])
    assert ResearchPlan.model_validate_json(plan.model_dump_json()) == plan


@pytest.mark.parametrize("query", ["", "   "])
def test_empty_research_topic_is_rejected(query: str) -> None:
    with pytest.raises(ValidationError):
        ResearchPlan(original_query=query, research_goal="A goal", tasks=[task(f"task-{n}") for n in range(1, 4)])


def test_empty_task_title_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ResearchTask(id="one", title="  ", objective="Objective")


def test_empty_task_objective_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ResearchTask(id="one", title="Title", objective="  ")


def test_duplicate_task_ids_are_rejected() -> None:
    with pytest.raises(ValidationError, match="unique"):
        ResearchPlan(original_query="A topic", research_goal="A goal", tasks=[task("same"), task("same"), task("other")])


@pytest.mark.parametrize("count", [2, 7])
def test_research_plan_task_count_is_bounded(count: int) -> None:
    with pytest.raises(ValidationError):
        ResearchPlan(original_query="A topic", research_goal="A goal", tasks=[task(f"task-{n}") for n in range(count)])
