.PHONY: tests

tests:
	PYTHONPATH=. python -m unittest discover tests
