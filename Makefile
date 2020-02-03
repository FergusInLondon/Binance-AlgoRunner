.PHONY: deps test

deps:
	pip install pandas
	pip install python-binance

test:
	python -m test.account
	python -m test.runner