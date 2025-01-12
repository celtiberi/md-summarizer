import logging
import re
from typing import List, Dict

from openai import AsyncOpenAI

from src.summarizer import APIAnalyzer, CodeSynthesizer
from .prompts.section_prompts import get_api_system_prompt, get_summarization_prompt, get_doc_processing_prompt
from .prompts.yaml_prompts import get_yaml_conversion_prompt, get_yaml_system_prompt
from .summarizer.types import APIInfo
from .summarizer.utils import count_tokens, format_api_info

# Based on OpenAI's documentation (https://platform.openai.com/docs/models)
MODEL_CONTEXT_WINDOW = {
    # GPT-4o Models (Latest)
    "gpt-4o": 128000,  # Versatile flagship model
    "gpt-4o-mini": 128000,  # Fast, affordable small model
    "o1": 128000,  # Reasoning model
    "o1-mini": 128000,  # Reasoning model, mini version

    # GPT-4 Models (Previous)
    "gpt-4-turbo-preview": 128000,  # Latest GPT-4 Turbo
    "gpt-4": 8192,  # Base GPT-4

    # GPT-3.5 Models
    "gpt-3.5-turbo": 16385,  # Now upgraded to 16k by default
    "gpt-3.5-turbo-16k": 16385,  # Explicit 16k version
    "gpt-3.5-turbo-instruct": 4096  # Instruct variant
}


class OpenAIClient:
    """Client for interacting with OpenAI API."""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """Initialize the client with API key and model.

        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-3.5-turbo)
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.logger = logging.getLogger(__name__)

        # Initialize components with same model
        self.analyzer = APIAnalyzer(self.client)
        self.synthesizer = CodeSynthesizer(self.client)

        # Get context window for model
        self.max_tokens = self._get_model_context_length(model)

    async def list_available_models(self) -> List[Dict]:
        """List supported models and their token limits."""
        models = []

        # Just use our hardcoded models
        for model_id, max_tokens in MODEL_CONTEXT_WINDOW.items():
            models.append({
                "id": model_id,
                "max_tokens": max_tokens
            })

        return sorted(models, key=lambda x: x['id'])

    def _get_model_context_length(self, model_name: str) -> int:
        """Get the context length for a model based on OpenAI's documentation."""
        if model_name not in MODEL_CONTEXT_WINDOW:
            raise ValueError(f"Unknown model: {model_name}. Please use one of: {', '.join(MODEL_CONTEXT_WINDOW.keys())}")
        return MODEL_CONTEXT_WINDOW[model_name]

    async def summarize_section(self, content: str, level: int, child_summaries: List[str] = None) -> str:
        """Summarize a section of documentation."""

        if not content or not content.strip():
            raise ValueError("content cannot be empty")

        # Check token count before sending
        token_count = count_tokens(content, model=self.model)
        if token_count > self.max_tokens:
            self.logger.warning("Content exceeds token limit: %d > %d",
                                token_count, self.max_tokens)
            raise ValueError(
                f"Content length ({token_count} tokens) exceeds model maximum ({self.max_tokens} tokens). "
                "Please reduce the size of the section."
            )

        # Get summary from model
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": get_api_system_prompt()},
                {"role": "user", "content": get_summarization_prompt(level, child_summaries)},
                {"role": "user", "content": f"Content:\n{content}\nLevel: {level}"}
            ],
            temperature=0.0
        )
        result = response.choices[0].message.content

        # Force header levels to be correct
        header_marker = '#' * level
        result = re.sub(r'^#{1,6}\s', f'{header_marker} ', result, flags=re.MULTILINE)
        return result

    def _contains_api_content(self, content: str) -> bool:
        """Check if content contains API-related information."""
        # Must have class or function definition
        has_definition = any(x in content.lower() for x in [
            "class ",
            "def ",
        ])

        # Must have API-related keywords
        has_api_keywords = any(x in content.lower() for x in [
            "method",
            "parameter",
            "returns",
            "exception"
        ])

        # Only treat as API content if both conditions are met
        is_api = has_definition and has_api_keywords
        self.logger.debug(f"Content is API documentation: {is_api}")

        return is_api

    async def convert_to_yaml(self, markdown: str) -> str:
        """Convert markdown to YAML format."""

        if not self.model or self.model == "invalid-model":
            raise ValueError("Failed to get response: Invalid model specified")

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": get_yaml_system_prompt()},
                {"role": "user", "content": get_yaml_conversion_prompt()},
                {"role": "user", "content": markdown}
            ],
            temperature=0.0
        )

        result = response.choices[0].message.content

        return result
