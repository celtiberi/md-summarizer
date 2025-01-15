from typing import Optional
from pydantic_ai import Agent
from pydantic_ai.usage import Usage
from pydantic import BaseModel
from ..agent.prompts import get_summarization_prompt, get_system_prompt
from ..config.settings import get_settings
import tiktoken

class SummarizeResult(BaseModel):
    """Result of summarization."""
    content: str

class SummarizerAgent:
    """Agent for summarizing text content using AI."""
    
    def __init__(self, system_prompt: Optional[str] = None, user_prompt: Optional[str] = None):
        """Initialize with API key and model."""
        self.usage = Usage()  # Track cumulative token usage
        self.settings = get_settings()
        
        # Store prompts
        self._system_prompt = system_prompt or get_system_prompt()
        self._user_prompt = user_prompt or get_summarization_prompt()
        
        # these will not be precise since a different model could be used
        # but should be good enough for our purposes
        self.system_prompt_tokens = self._count_tokens_openai(self._system_prompt)
        self.document_prompt_tokens = self._count_tokens_openai(self._user_prompt)
        
        # Initialize AI agent
        self.agent = Agent(
            get_settings().model,
            result_type=SummarizeResult,
            system_prompt=self._system_prompt,
        )

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

    @property
    def system_prompt(self) -> str:
        """Get the current system prompt."""
        return self._system_prompt
    
    @system_prompt.setter
    def system_prompt(self, prompt: str):
        """Set a custom system prompt."""
        self._system_prompt = prompt
        self.system_prompt_tokens = self._count_tokens_openai(prompt)
        self.agent = Agent(
            get_settings().model,
            result_type=SummarizeResult,
            system_prompt=prompt,
        )
    
    @property
    def user_prompt(self) -> str:
        """Get the current user prompt template."""
        return self._user_prompt
    
    @user_prompt.setter
    def user_prompt(self, prompt: str):
        """Set a custom user prompt template."""
        self._user_prompt = prompt
        self.document_prompt_tokens = self._count_tokens_openai(prompt)

    async def run(self, content: str) -> str:
        """Run the agent and update usage statistics."""
        if not content.strip():
            return content
            
        # Use the custom user prompt
        user_prompt = self._user_prompt + "\n\n" + content
        
        result = await self.agent.run(user_prompt=user_prompt)
        
        self.update_usage(result)
        return result.data.content 
       