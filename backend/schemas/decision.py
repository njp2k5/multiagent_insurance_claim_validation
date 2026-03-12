from pydantic import BaseModel
from typing import List
from schemas.agent import AgentResponse

class FinalDecisionResponse(BaseModel):
    claim_id: str
    final_decision: str
    final_confidence: float
    agent_results: List[AgentResponse]
