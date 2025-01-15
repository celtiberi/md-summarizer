.PHONY: test clean build publish release

test:
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
	twine check dist/*

# Publishing is handled by GitHub workflows:
# - .github/workflows/publish.yml for PyPI
# - .github/workflows/publish-test.yml for TestPyPI
