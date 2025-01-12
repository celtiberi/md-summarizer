import json
from typing import Dict, Any
from openai import AsyncOpenAI
from .types import APIInfo, Class, Method, Parameter

class APIAnalyzer:
    """Analyzes documentation to extract API information."""
    
    def __init__(self, client: AsyncOpenAI):
        self.client = client
        
    async def analyze(self, content: str) -> APIInfo:
        """Extract API information from documentation."""
        prompt = """Analyze this documentation and extract API information.
        Return ONLY a JSON object matching this structure:
        {
            "classes": [{
                "name": str,
                "description": str,
                "methods": [{
                    "name": str,
                    "description": str,
                    "params": [{"name": str, "type": str, "default": str}],
                    "returns": str,
                    "exceptions": [str]
                }]
            }],
            "functions": [similar structure]
        }
        
        Guidelines:
        - Include ALL public methods and functions
        - Document ALL parameters and types
        - Note ALL exceptions that can be raised
        - Keep descriptions brief and technical
        - Include return types for all methods
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": content}
            ],
            temperature=0.0
        )
        
        # Parse JSON response
        api_data = json.loads(response.choices[0].message.content)
        
        # Convert to typed objects
        return self._parse_api_info(api_data)
    
    def _parse_api_info(self, data: Dict[str, Any]) -> APIInfo:
        """Convert JSON data to typed APIInfo object."""
        classes = [
            Class(
                name=c["name"],
                description=c.get("description"),
                methods=[
                    Method(
                        name=m["name"],
                        description=m.get("description"),
                        params=[
                            Parameter(
                                name=p["name"],
                                type=p["type"],
                                default=p.get("default"),
                                description=p.get("description")
                            )
                            for p in m["params"]
                        ],
                        returns=m["returns"],
                        exceptions=m["exceptions"]
                    )
                    for m in c["methods"]
                ]
            )
            for c in data["classes"]
        ]
        
        functions = [
            Method(
                name=f["name"],
                description=f.get("description"),
                params=[
                    Parameter(
                        name=p["name"],
                        type=p["type"],
                        default=p.get("default"),
                        description=p.get("description")
                    )
                    for p in f["params"]
                ],
                returns=f["returns"],
                exceptions=f["exceptions"]
            )
            for f in data["functions"]
        ]
        
        return APIInfo(classes=classes, functions=functions) 