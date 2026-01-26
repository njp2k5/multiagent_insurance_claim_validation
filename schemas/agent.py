from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class AgentResponse(BaseModel):
    agent_name: str
    status: str
    confidence: float
    message: str
    metadata: Dict[str, Any]


class InconsistencyDetail(BaseModel):
    field: str
    source1: str
    value1: Any
    source2: str
    value2: Any
    similarity: Optional[float] = None
    threshold: Optional[float] = None
    difference: Optional[int] = None


class CrossValidationResponse(BaseModel):
    status: str  # VERIFIED | MISMATCH | PARTIAL_MATCH | INSUFFICIENT_DATA
    name_match: bool
    age_match: bool
    inconsistencies: List[InconsistencyDetail]
    confidence: float
    message: str


class CrossAgentDataResponse(BaseModel):
    identity_name: Optional[str] = None
    identity_age: Optional[int] = None
    identity_aadhaar: Optional[str] = None
    document_name: Optional[str] = None
    document_age: Optional[int] = None
    claim_form_name: Optional[str] = None
    claim_form_age: Optional[int] = None


class FullCrossValidationResponse(BaseModel):
    cross_validation: CrossValidationResponse
    agent_data: CrossAgentDataResponse
    fraud_result: Optional[AgentResponse] = None
