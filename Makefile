.PHONY: setup env install dev test lint run preview check clean help

VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

help: ## 도움말
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

setup: $(VENV) env install ## 전체 초기 설정 (venv + .env + 의존성)
	@echo "\n✅ 설정 완료! .env 파일의 API 키를 채워주세요."
	@echo "   make run TOPIC='주제' 로 실행할 수 있습니다.\n"

$(VENV):
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip -q

env: ## .env 파일 생성 (.env.example 복사)
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "📝 .env 파일 생성됨 — API 키를 채워주세요"; \
	else \
		echo "⏭  .env 이미 존재합니다"; \
	fi

install: $(VENV) ## 의존성 설치 (런타임)
	$(PIP) install -e . -q

dev: $(VENV) ## 개발 의존성 설치 (런타임 + 테스트 + 린트)
	$(PIP) install -e ".[dev]" -q

test: ## 테스트 실행
	$(PY) -m pytest tests/ -v --tb=short

lint: ## ruff 린트
	$(PY) -m ruff check src/ tests/

lint-fix: ## ruff 자동 수정
	$(PY) -m ruff check --fix src/ tests/

run: ## ppt-maker 실행 (TOPIC 필수, 예: make run TOPIC='AI 트렌드')
	@if [ -z "$(TOPIC)" ]; then \
		echo "❌ TOPIC을 지정하세요: make run TOPIC='AI 트렌드 2025'"; \
		exit 1; \
	fi
	$(VENV)/bin/ppt-maker generate "$(TOPIC)"

run-no-llm: ## LLM 없이 실행 (make run-no-llm TOPIC='주제')
	@if [ -z "$(TOPIC)" ]; then \
		echo "❌ TOPIC을 지정하세요: make run-no-llm TOPIC='테스트 주제'"; \
		exit 1; \
	fi
	$(VENV)/bin/ppt-maker generate "$(TOPIC)" --no-research

preview: ## 마크다운만 생성 (make preview TOPIC='주제')
	@if [ -z "$(TOPIC)" ]; then \
		echo "❌ TOPIC을 지정하세요: make preview TOPIC='주제'"; \
		exit 1; \
	fi
	$(VENV)/bin/ppt-maker preview "$(TOPIC)"

check: ## 환경 검증 (pandoc, 폰트, 템플릿)
	$(VENV)/bin/ppt-maker check

clean: ## 빌드 아티팩트 정리
	rm -rf output/ dist/ build/ *.egg-info .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

clean-all: clean ## 전체 정리 (venv 포함)
	rm -rf $(VENV)
