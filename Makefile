.PHONY: deps test

lint:
	flake8 ./lib --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 ./lib --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

deps:
	pip install pandas
	pip install python-binance
	pip install flake8

test:
	python -m test.account
	python -m test.runner