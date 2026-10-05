.SILENT:
.PHONY: install run debug clean lint lint-strict

MAIN := RAG
VENV := ".venv"
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
FLAKE8 := $(VENV)/bin/flake8
MYPY := $(VENV)/bin/mypy
ModuleFile := FlyIn
SIZE := 2000

install:
	@echo "Installing Project $(MAIN)"
	python3 -m venv $(VENV)

	mkdir -p $(HOME)/goinfre/$(MAIN)
	export HF_HOME=$(HOME)/goinfre/$(MAIN)
	export UV_CACHE_DIR=$(HOME)/goinfre/$(MAIN)

	$(PIP) install --upgrade pip
	$(PIP) install poetry uv
	$(VENV)/bin/uv sync

run:
	echo "Running Project $(MAIN)"
	$(VENV)/bin/uv run python -m src index -max_chunk_size 2000

debug:
	$(PYTHON) -m pdb $(MAIN)

lclean:
	rm -rf src/*/__pycache__ src/__pycache__
	rm -rf .mypy_cache
	rm -rf data/output/search_results/AnsweredQuestions/*.json
	rm -rf data/results/*.json
	rm -rf data/processed/*.json

clean: lclean
	rm -rf $(VENV)
	rm -rf __pycache__ .mypy_cache .pytest_cache $(ModuleFile)/__pycache__ .vscode $(RESULTFILE) .venv poetry.lock uv.lock
	rm -rf $(HOME)/goinfre/$(MAIN)

test:
	.venv/bin/uv run python -m src index -max_chunk_size 2000
	.venv/bin/uv run python -m src search_dataset -dataset_path data/UnansweredQuestions/dataset_code_public.json -k 10 -save_directory data/output/search_results/AnsweredQuestions/test.json
	./moulinette evaluate_student_search_results data/output/search_results/AnsweredQuestions/test.json data/AnsweredQuestions/dataset_code_public.json
	rm data/output/search_results/AnsweredQuestions/test.json
	.venv/bin/uv run python -m src index -max_chunk_size 2000
	.venv/bin/uv run python -m src search_dataset -dataset_path data/UnansweredQuestions/dataset_docs_public.json -k 10 -save_directory data/output/search_results/AnsweredQuestions/test.json
	./moulinette evaluate_student_search_results data/output/search_results/AnsweredQuestions/test.json data/AnsweredQuestions/dataset_docs_public.json

lint:
	$(MYPY) ./src --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
	$(FLAKE8) ./src

lint-strict:
	$(MYPY) ./src --strict
	$(FLAKE8) ./src