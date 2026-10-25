"""Validated data exchanged by research agents."""

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ResearchTask(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    objective: str = Field(min_length=1)

    @field_validator("id", "title", "objective")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value


class ResearchPlan(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    original_query: str = Field(min_length=1)
    research_goal: str = Field(min_length=1)
    tasks: list[ResearchTask] = Field(min_length=3, max_length=6)

    @field_validator("original_query", "research_goal")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value

    @model_validator(mode="after")
    def task_ids_must_be_unique(self) -> "ResearchPlan":
        ids = [task.id for task in self.tasks]
        if len(ids) != len(set(ids)):
            raise ValueError("research task IDs must be unique")
        return self
