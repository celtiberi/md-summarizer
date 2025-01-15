import pytest
import os
from md_summarizer import MarkdownSummarizer, MarkdownParser
from md_summarizer.agent import SummarizerAgent
import logging

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment and load test settings.
    
    This fixture runs automatically once per test session and:
    1. Sets ENV to 'test'
    2. Loads .env.test file
    3. Verifies required settings are available
    """
    
    # Set test environment BEFORE importing settings
    os.environ["ENV"] = "test"
    
    # Now import settings
    from md_summarizer.config.settings import get_settings
    
    yield get_settings()

@pytest.fixture
def parser():
    """Create a parser with default settings."""
    return MarkdownParser()

@pytest.fixture
async def agent():
    """Create Agent for testing."""
    return SummarizerAgent()

@pytest.fixture
def summarizer(setup_test_environment):
    """Create converter with test configuration.
    
    Should:
    1. Create converter with test settings
    2. Initialize parser and client
    
    Returns:
        MarkdownToYamlConverter: Test configuration
    """
    
    return MarkdownSummarizer(agent=SummarizerAgent())

@pytest.fixture(autouse=True)
def setup_logging(setup_test_environment):
    """Configure logging for tests."""
    # Get log level from settings
    log_level = getattr(logging, setup_test_environment.log_level.upper())
    
    formatter = logging.Formatter('%(message)s')
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Silence http client logs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    # Remove any existing handlers
    root_logger.handlers = []
    
    # Add our clean formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler) 