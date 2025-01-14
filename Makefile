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

publish: build
	python -m twine upload --repository testpypi dist/* --non-interactive 

release: clean bump-version build publish
	@echo "Released version $(shell python -c "from pathlib import Path; import re; match = re.search(r'version = \"(\d+\.\d+\.\d+)\"', Path('pyproject.toml').read_text()); print(match.group(1) if match else 'unknown')")" 