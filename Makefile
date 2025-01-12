.PHONY: test test-converter test-parser test-openai clean

# Variables
PYTHON = python3
PYTEST = pytest -v
TEST_DIR = tests

# Test targets
test:
	$(PYTEST) $(TEST_DIR)

test-basic:
	$(PYTEST) tests/test_md_summarizer.py::test_basic_summarization -v -s

test-converter:
	$(PYTEST) $(TEST_DIR)/test_converter.py

test-parser:
	$(PYTEST) $(TEST_DIR)/test_md_parser.py

test-openai:
	$(PYTEST) $(TEST_DIR)/test_openai_client.py

# Clean up cache files
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete 