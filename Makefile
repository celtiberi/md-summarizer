.PHONY: test clean build publish

test:
	pytest -v -s --log-cli-level=INFO

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

publish: build
	python -m twine upload --repository testpypi dist/* 
