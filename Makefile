clean:
	rm -rf src/syntactes/__pycache__ src/syntactes/tests/__pycache__ src/syntactes/parser/__pycache__ src/syntactes/parsing_table/__pycache__
	rm -rf dist src/syntactes.egg-info

test:
	python -m unittest discover -v src/syntactes/tests/

install-local-package:
	pip install -e .

build-package:
	python -m build

upload-package:
	python -m twine upload --verbose -u '__token__' dist/*
