clean:
	rm -rf src/syntactes/__pycache__ src/syntactes/tests/__pycache__

test:
	python -m unittest discover -v src/syntactes/tests/

install-local-package:
	pip install -e .
