.PHONY: install

install:
	poetry install

lint:
	poetry run mypy quadipy
	poetry run flake8 quadipy
	poetry run black --check quadipy

test: lint
	poetry run python -m pytest

setup:
	make install
	poetry run pre-commit install
	make test
