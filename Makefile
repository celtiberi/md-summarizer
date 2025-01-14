.PHONY: test clean build publish

.PHONY: test clean build publish

test:
	pytest -v -s --log-cli-level=INFO

	pytest -v -s --log-cli-level=INFO

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

bump-version:
	python scripts/bump_version.py

build: clean bump-version
	python -m build

publish: build
	python -m twine upload --repository testpypi dist/* --non-interactive 