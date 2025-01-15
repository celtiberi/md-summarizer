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

publish-test: build
	python -m twine upload --repository testpypi dist/* --non-interactive 

publish: build
	python -m twine upload dist/* --verbose

release-test: publish-test
	twine upload dist/*
	@echo "Released test version $(shell python -c "from pathlib import Path; import re; match = re.search(r'version = \"(\d+\.\d+\.\d+)\"', Path('pyproject.toml').read_text()); print(match.group(1) if match else 'unknown')")" 

release: publish
	twine upload dist/*
	@echo "Released version $(shell python -c "from pathlib import Path; import re; match = re.search(r'version = \"(\d+\.\d+\.\d+)\"', Path('pyproject.toml').read_text()); print(match.group(1) if match else 'unknown')")"
