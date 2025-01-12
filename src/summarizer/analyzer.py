from typing import List, Optional
from openai import AsyncOpenAI
from .types import APIInfo, Class, Method, Parameter

class APIAnalyzer:
    """Analyzes documentation for API information."""
    
    def __init__(self, client: AsyncOpenAI):
        self.client = client
    
    async def analyze(self, content: str) -> APIInfo:
        """Analyze documentation content for API information."""
        if not self.client:
            raise Exception("API client is not initialized")
            
        try:
            if not hasattr(self.client, 'chat') or not hasattr(self.client.chat, 'completions'):
                raise Exception("Invalid API client configuration")
            
            prompt = """Extract API information from this documentation.
            Include:
            - Class definitions
            - Method signatures
            - Parameters and types
            - Return types
            - Exceptions
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract API information from documentation."},
                    {"role": "user", "content": prompt},
                    {"role": "user", "content": content}
                ],
                temperature=0.0
            )
            
            # Process response and create APIInfo
            # ...
            
        except Exception as e:
            raise Exception(f"Failed to analyze API: {str(e)}") 