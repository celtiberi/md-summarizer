.PHONY: test test-converter test-parser test-openai clean

# Variables
PYTHON = python3
PYTEST = pytest -v
TEST_DIR = tests

# Test settings
LOG_LEVEL ?= INFO

# Test targets
test:
	$(PYTEST) $(TEST_DIR) -s --log-cli-level=$(LOG_LEVEL)

test-basic:
	$(PYTEST) tests/test_md_summarizer.py::test_basic_summarization -v -s

test-converter:
	$(PYTEST) $(TEST_DIR)/test_converter.py

test-parser:
	$(PYTEST) $(TEST_DIR)/test_md_parser.py

test-openai:
	$(PYTEST) $(TEST_DIR)/test_openai_client.py

# Run specific test case
test-case:
	$(PYTEST) -v -s --log-cli-level=$(LOG_LEVEL) -k $(TEST)

# Clean up cache files
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete 