.PHONY: env-check build lint deps test run todo

help:           ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

env-check:		## Check that the current environment is capable of running AlgoRunner.
	@sh setup.sh

build:			## Build docker image, tagged "algorunner:<commit>"
	echo "build docker container"

lint:			## Run code quality checks
	poetry run flake8

deps:			## Install all required dependencies (including for development)
	poetry install --no-interaction

test:			## Run all tests - including both unit tests and BDD scenarios
	poetry run pytest
	poetry run behave

run:			## Run AlgoRunner
	poetry run python run.py

todo:			## Scan the codebase for items tagged with "@todo"
	@grep -r "@todo" --exclude=\*.pyc algorunner
	echo "\nTotal items marked '@todo': `grep --exclude=\*.pyc -r '@todo' . | wc -l | xargs`."
