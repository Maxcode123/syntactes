.PHONY: clean test install-local-package build-package upload-package

clean:
	rm -rf src/syntactes/__pycache__ src/syntactes/tests/__pycache__ src/syntactes/parser/__pycache__ src/syntactes/parsing_table/__pycache__
	rm -rf dist src/syntactes.egg-info

test:
	uv run python -m unittest discover -v src/syntactes/tests/

install-local-package:
	uv pip install -e .

build-package:
	uv build

upload-package:
	uv publish
