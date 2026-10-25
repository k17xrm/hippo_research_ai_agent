# Research Hippo v0.1.0

Research Hippo는 사용자의 연구 질문을 여러 조사 과제로 분해하는 Python 기반 범용 AI Research Assistant입니다. 최종적으로 Planner, Search, Analysis, Critic Agent가 협업하는 시스템을 목표로 하며, v0.1.0은 발표 가능한 Planner Agent MVP에 집중합니다.

> 현재 출력은 문헌 검색 결과나 검증된 연구 동향이 아니라 **향후 문헌 조사를 위한 연구 계획**입니다.

## 아키텍처와 현재 범위

```text
User → Rich CLI / Textual TUI → ResearchOrchestrator
                                  ↓
                            PlannerAgent
                                  ↓
                    Ollama 또는 Mock LLM Client
                                  ↓
                    Pydantic ResearchPlan 검증
                                  ↓
                         ResearchState → UI
```

현재 구현:

- 입력 언어와 연구 분야에 맞춰 3~6개 조사 과제를 만드는 Planner Agent
- Pydantic v2 기반 스키마, 중복 ID 및 공백 검증
- 세션별 ResearchState와 UI 독립적인 AgentEvent
- Ollama Structured Outputs 연동
- API 없이 동작하는 입력 대응형 Mock Demo Mode
- Rich CLI와 비동기 Worker 기반 Textual TUI
- 재사용 가능한 분홍색 하마 AgentCard
- 네트워크가 필요 없는 pytest 테스트

Search, Analysis, Critic Agent와 논문 검색, 데이터베이스는 이번 버전의 실행 흐름에 포함되지 않습니다. 저장소의 관련 파일은 향후 확장을 위한 기존 골격이며 Planner MVP에서 호출하지 않습니다.

## 폴더 구조

```text
agents/       BaseAgent, PlannerAgent
config/       환경변수 설정
core/         Orchestrator, State, Event
llm/          Ollama/Mock LLM Client
prompts/      코드와 분리된 Planner Prompt
schemas/      Pydantic 전달 모델
ui/           Rich CLI 및 Textual TUI
tests/        단위·통합 테스트
main.py       argparse 실행 진입점
```

## 설치

Python 3.11 이상이 필요합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

## 환경변수

로컬 Ollama를 사용할 때 `.env`로 모델과 서버 주소를 설정합니다.

```bash
cp .env.example .env
```

```dotenv
LLM_PROVIDER=ollama
LLM_MODEL=qwen3:8b
LLM_TIMEOUT=120
OLLAMA_HOST=http://127.0.0.1:11434
```

## 실행

기본 모드는 TUI입니다.

```bash
python main.py
python main.py --tui
python main.py --cli
```

API 키와 네트워크 없이 발표용 Demo Mode를 실행할 수 있습니다.

```bash
python main.py --tui --mock
python main.py --cli --mock
```

`--cli`와 `--tui`는 동시에 사용할 수 없으며 argparse가 오류를 출력합니다. LIVE 모드에서 Ollama 서버 또는 모델에 연결하지 못하면 오류를 안내합니다.

## 테스트

일반 테스트는 실제 Ollama 서버를 호출하지 않습니다.

```bash
pytest -q
```

CLI를 빠르게 확인하려면 다음처럼 입력을 전달할 수 있습니다.

```bash
printf 'Vision Transformer의 최근 연구 동향\n' | python main.py --cli --mock
```

## 향후 개발 계획

1. ResearchTask별 검색어를 만들고 arXiv/Semantic Scholar 어댑터를 호출하는 Search Agent 추가
2. 출처와 원문 식별자를 보존하는 Paper schema 구축
3. 논문 섹션별 근거를 추출하는 Analysis Agent 추가
4. 주장-근거 일관성과 누락을 판정하는 Critic Agent 및 제한된 재검색 루프 추가
5. 영속 저장소, 재개 가능한 세션, 평가와 관측성 도입

새 Agent는 BaseAgent의 비동기 실행 및 동일한 AgentEvent 계약을 사용하고 Orchestrator에 단계적으로 연결할 수 있습니다.
