.PHONY: test demo
test:
	python -m unittest discover -s tests -v
demo:
	python -m cell_validation --output-dir results
