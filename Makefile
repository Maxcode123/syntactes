.PHONY: clean test lint format type-check install-local-package build-package upload-package start-doc-server deploy-documentation

clean:
	rm -rf src/syntactes/__pycache__ src/syntactes/tests/__pycache__ src/syntactes/parser/__pycache__ src/syntactes/parsing_table/__pycache__
	rm -rf dist src/syntactes.egg-info

test:
	uv run python -m unittest discover -v src/syntactes/tests/

lint:
	uv run ruff check src

format:
	uv run ruff format src examples

type-check:
	uv run ty check src

install-local-package:
	uv pip install -e .

build-package:
	uv build

upload-package:
	uv publish

start-doc-server:
	uv run python -m mkdocs serve

deploy-documentation:
	uv run python -m mkdocs gh-deploy --config-file mkdocs.yml
