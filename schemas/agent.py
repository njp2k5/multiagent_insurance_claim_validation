from pydantic import BaseModel
from typing import Dict, Any

class AgentResponse(BaseModel):
    agent_name: str
    status: str
    confidence: float
    message: str
    metadata: Dict[str, Any]
