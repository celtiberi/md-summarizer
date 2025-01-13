from typing import Optional, Dict
from pydantic_ai import Agent, RunContext
from pydantic_ai.usage import Usage
from pydantic import BaseModel
from src.agent.prompts import get_summarization_prompt, get_system_prompt
from src.config.settings import get_settings
import tiktoken
from anthropic import Anthropic
from transformers import AutoTokenizer

class BaseAgent:
    """Base agent with token management and usage tracking."""
    
    def __init__(self):
        """Initialize with API key and model."""
        self.usage = Usage()  # Track cumulative token usage
        self.settings = get_settings()

        # these will not be precise since a different model could be used
        # but should be good enough for our purposes
        self.system_prompt_tokens = self._count_tokens_openai(get_system_prompt())
        self.document_prompt_tokens = self._count_tokens_openai(get_summarization_prompt())
        
    def _count_tokens_openai(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """Count tokens for OpenAI models using tiktoken. 
        Args:
            text: Text to count tokens for
            model: Model name to use encoding for, defaults to gpt-3.5-turbo
            
        Returns:
            Number of tokens in text
        """
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    
    
    def update_usage(self, result) -> None:
        """Update usage statistics."""
        usage_data = Usage(
            # Count this as one API request
            requests=1,
            
            # Input tokens used in the document section being summarized
            # we need to subtract the system and document prompt tokens.  
            #   - this is because our goal is to measure only the tokens from the section
            #     being summarized
            request_tokens=result.usage().request_tokens - self.system_prompt_tokens - self.document_prompt_tokens,
            
            # Output tokens generated in the response
            response_tokens=result.usage().response_tokens,
            
            # Total tokens = input + output
            total_tokens=result.usage().total_tokens
        )
        
        # Add to running totals
        self.usage.incr(usage_data)

class SummarizeResult(BaseModel):
    """Result of summarization."""
    content: str

class DocumentAgent(BaseAgent):
    """Agent for summarizing markdown documents."""
    
    def __init__(self):
        """Initialize with API key and model."""
        super().__init__()
        
        self.agent = Agent(
            get_settings().model,
            result_type=SummarizeResult,
            system_prompt=get_system_prompt(),
        )

    async def summarize_section(
        self, 
        content: str
    ) -> str:
        """Summarize a section of content."""
        
        user_prompt = get_summarization_prompt() + "\n\n" + content
        
        result = await self.agent.run(
            user_prompt=user_prompt
        )
        
        # Update usage statistics
        self.update_usage(result)
        
        return result.data.content 
       