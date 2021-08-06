.PHONY: env-check build lint deps test run

env-check:
	@sh setup.sh

build:
	echo "build docker container"

lint:
	poetry run flake8

deps:
	poetry install --no-interaction

test:
	poetry run pytest
	poetry run behave

run:
	poetry run python run.py
