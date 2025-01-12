from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Parameter:
    """Represents a method/function parameter."""
    name: str
    type: str
    default: Optional[str] = None
    description: Optional[str] = None

@dataclass
class Method:
    """Represents a method or function."""
    name: str
    params: List[Parameter]
    returns: str
    exceptions: List[str]
    description: Optional[str] = None

@dataclass
class Class:
    """Represents a class definition."""
    name: str
    methods: List[Method]
    description: Optional[str] = None

@dataclass
class APIInfo:
    """Complete API information extracted from documentation."""
    classes: List[Class]
    functions: List[Method] 