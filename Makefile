.PHONY: env-check build lint deps test run todo

help:				## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

env-check:			## Check that the current environment is capable of running AlgoRunner.
	@sh setup.sh

build:				## Build docker image, tagged "algorunner:<commit>" and "algorunner:latest"
	docker build -t algorunner:latest -t algorunner:`git rev-parse --short HEAD` .

docker: build			## Run the docker image after it's built.
	docker run algorunner:latest

lint:				## Run code quality checks
	poetry run flake8

deps: env-check			## Install all required dependencies (including for development)
	poetry install --no-interaction

test:				## Run all tests - including both unit tests and BDD scenarios
	poetry run pytest
	poetry run behave

local:				## Run AlgoRunner locally via Poetry
	poetry run python run.py

todo:				## Scan the codebase for items tagged with "@todo"
	@grep -r "@todo" --exclude=\*.pyc algorunner
	@echo "\nTotal items marked '@todo': `grep --exclude=\*.pyc -r '@todo' . | wc -l | xargs`."
