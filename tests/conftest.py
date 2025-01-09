import os
import pytest
from src.md_parser import MarkdownParser
from src.openai_client import OpenAIClient
from src.converter import MarkdownToYamlConverter
from src.config.settings import Settings, EnvironmentType, PROJECT_ROOT
from dotenv import load_dotenv

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment and load test settings.
    
    This fixture runs automatically once per test session and:
    1. Sets ENV to 'test'
    2. Loads .env.test file
    3. Verifies required settings are available
    """
    # Set test environment
    os.environ["ENV"] = EnvironmentType.TEST.value
    
    # Load test environment file
    test_env_file = os.path.join(PROJECT_ROOT, ".env.test")
    if not os.path.exists(test_env_file):
        raise RuntimeError(f"Test environment file not found: {test_env_file}")
    
    load_dotenv(test_env_file, override=True)
    
    # Verify settings load correctly
    settings = Settings(env=EnvironmentType.TEST)
    assert settings.is_test
    
    yield settings

@pytest.fixture
def parser():
    """Create a parser with default settings."""
    return MarkdownParser(max_tokens=2000)

@pytest.fixture
def small_parser():
    """Create a parser with small token limit.
    
    Should:
    1. Create parser with small max_tokens for testing splits
    2. Use default min_section_level
    
    Returns:
        MarkdownParser: Small token configuration
    """
    return MarkdownParser(max_tokens=50)

@pytest.fixture
def client(setup_test_environment):
    """Create OpenAI client with test configuration.
    
    Should:
    1. Create client with test API key
    2. Use default model and retry settings
    
    Returns:
        OpenAIClient: Test configuration
    """
    return OpenAIClient(
        api_key=setup_test_environment.openai_api_key,
        model=setup_test_environment.openai_model
    )

@pytest.fixture
def converter(setup_test_environment):
    """Create converter with test configuration.
    
    Should:
    1. Create converter with test settings
    2. Initialize parser and client
    
    Returns:
        MarkdownToYamlConverter: Test configuration
    """
    return MarkdownToYamlConverter(
        api_key=setup_test_environment.openai_api_key,
        model=setup_test_environment.openai_model
    )

@pytest.fixture
def example_markdown():
    """Provide example markdown content with edge cases.
    
    Should:
    1. Include multiple header levels
    2. Include code blocks
    3. Include special characters and formatting
    4. Include lists and nested content
    
    Returns:
        str: Example markdown content
    """
    return """# Main Title
This is the main content with *formatting*.

## Section 1
Some content here with special chars: & < > "

    def example():
        # With comments
        return True

## Section 2
1. Numbered list
2. With items

### Subsection
- Bullet list
- With items
""" 