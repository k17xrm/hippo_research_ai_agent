"""Provider-independent interface and Ollama/Mock implementations."""

import asyncio
import json
from abc import ABC, abstractmethod
from typing import Any

from pydantic import ValidationError

from config.settings import Settings
from schemas.research import ResearchPlan


class LLMError(RuntimeError):
    """An actionable, user-facing LLM failure."""


class LLMClient(ABC):
    @abstractmethod
    async def generate_plan(self, query: str, system_prompt: str) -> Any:
        """Return data that can be validated as a ResearchPlan."""


def _parse_research_plan_response(raw_plan: str, query: str) -> ResearchPlan:
    """Accept the direct schema and Qwen's nested research-plan variant."""
    payload = json.loads(raw_plan)
    if not isinstance(payload, dict):
        raise ValueError("The Ollama response must be a JSON object.")

    nested_plan = payload.get("research_plan")
    if isinstance(nested_plan, dict):
        normalized_tasks = []
        for task in nested_plan.get("tasks", []):
            if not isinstance(task, dict):
                normalized_tasks.append(task)
                continue
            normalized_task = dict(task)
            if "objective" not in normalized_task and "objectives" in normalized_task:
                normalized_task["objective"] = normalized_task["objectives"]
            normalized_tasks.append(normalized_task)

        payload = {
            "original_query": query,
            "research_goal": (
                nested_plan.get("research_goal")
                or nested_plan.get("objective")
                or nested_plan.get("title")
            ),
            "tasks": normalized_tasks,
        }

    return ResearchPlan.model_validate(payload)


class MockLLMClient(LLMClient):
    async def generate_plan(self, query: str, system_prompt: str) -> dict[str, Any]:
        del system_prompt
        await asyncio.sleep(0)  # yield control without inventing a fake delay
        korean = any("가" <= char <= "힣" for char in query)
        if korean:
            goal = f"'{query}'에 관한 체계적인 문헌 조사를 위한 범위와 관점을 정의한다."
            tasks = [
                ("개념 및 범위 정립", "핵심 개념, 용어, 연구 범위와 평가 기준을 정의한다."),
                ("주요 접근법과 발전 과정", "대표적인 접근법과 시간에 따른 연구 방향의 변화를 조사한다."),
                ("방법론 및 평가 비교", "사용되는 방법론, 데이터, 실험 설계와 평가 지표를 비교한다."),
                ("한계와 향후 연구", "현재 연구의 한계, 미해결 문제와 유망한 후속 연구를 파악한다."),
            ]
        else:
            goal = f"Define a systematic literature-review scope and perspectives for: {query}"
            tasks = [
                ("Concepts and scope", "Define key concepts, terminology, scope, and evaluation criteria."),
                ("Major approaches and evolution", "Investigate major approaches and how the field has evolved."),
                ("Methods and evaluation", "Compare methods, datasets, experimental designs, and metrics."),
                ("Limitations and future work", "Identify limitations, open problems, and promising directions."),
            ]
        return {
            "original_query": query,
            "research_goal": goal,
            "tasks": [
                {"id": f"task-{index}", "title": title, "objective": objective}
                for index, (title, objective) in enumerate(tasks, start=1)
            ],
        }


class OllamaLLMClient(LLMClient):
    def __init__(self, settings: Settings) -> None:
        if settings.llm_provider != "ollama":
            raise LLMError(f"Unsupported LLM provider: {settings.llm_provider}")
        self.settings = settings

    async def generate_plan(self, query: str, system_prompt: str) -> ResearchPlan:
        try:
            from ollama import AsyncClient

            client = AsyncClient(
                host=self.settings.ollama_host,
                timeout=self.settings.llm_timeout,
            )
            async with asyncio.timeout(self.settings.llm_timeout):
                response = await client.chat(
                    model=self.settings.llm_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query},
                    ],
                    format=ResearchPlan.model_json_schema(),
                    options={"temperature": 0},
                    think=False,
                )
            if not response.message.content:
                raise LLMError("The LLM returned no valid research plan.")
            return _parse_research_plan_response(response.message.content, query)
        except LLMError:
            raise
        except (json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
            raise LLMError("Ollama returned an invalid research plan.") from exc
        except TimeoutError as exc:
            raise LLMError(
                f"The Ollama request timed out after {self.settings.llm_timeout:g} seconds."
            ) from exc
        except Exception as exc:
            raise LLMError(f"Ollama request failed: {exc}") from exc


def create_llm_client(settings: Settings, mock: bool = False) -> LLMClient:
    return MockLLMClient() if mock else OllamaLLMClient(settings)
