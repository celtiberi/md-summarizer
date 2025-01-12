from openai import AsyncOpenAI
from .types import APIInfo
from .utils import format_api_info

class DocProcessor:
    """Creates final documentation combining API info and examples."""
    
    def __init__(self, client: AsyncOpenAI):
        self.client = client
    
    async def process(self, content: str, api_info: APIInfo, examples: str) -> str:
        """Create final documentation."""
        prompt = """Create concise technical documentation following these rules:
        
        Format:
        1. Brief Overview (2-3 sentences)
        2. API Signatures (from provided info)
        3. Code Examples (use provided examples)
        4. Technical Notes (if any)
        
        Guidelines:
        - Remove tutorial content
        - Keep technical relationships
        - Maintain markdown formatting
        - Aim for 50-70% reduction
        - Keep ALL code examples
        - Preserve exact syntax
        
        Output Format:
        ### [Title]
        [Overview]
        
        [Code Blocks]
        
        [Technical Notes]
        """
        
        # Format inputs
        api_str = self._format_api_info(api_info)
        
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Original:\n{content}\n\nAPI Info:\n{api_str}\n\nExamples:\n{examples}"}
            ],
            temperature=0.0
        )
        
        return response.choices[0].message.content
    
    def _format_api_info(self, api_info: APIInfo) -> str:
        return format_api_info(api_info) 