from typing import TypedDict, List, Dict, Any, Optional


class AgentResult(TypedDict):
    agent_name: str
    status: str        # PASS | FAIL | FLAG | INFO
    confidence: float
    message: str
    metadata: Dict[str, Any]


class CrossAgentData(TypedDict, total=False):
    """Data extracted by different agents for cross-validation."""
    # Identity agent extracted data
    identity_name: Optional[str]
    identity_age: Optional[int]
    identity_aadhaar: Optional[str]
    
    # Document agent extracted data
    document_name: Optional[str]
    document_age: Optional[int]
    
    # Claim form data
    claim_form_name: Optional[str]
    claim_form_age: Optional[int]


class CrossValidationResult(TypedDict, total=False):
    """Result of cross-validation between different agents."""
    status: str  # VERIFIED | MISMATCH | PARTIAL_MATCH | INSUFFICIENT_DATA
    name_match: bool
    age_match: bool
    inconsistencies: List[Dict[str, Any]]
    confidence: float
    message: str


class ClaimState(TypedDict, total=False):
    user_id: str
    user_email: str
    is_authenticated: bool

    claim_id: Optional[str]
    claim_form: Optional[Dict[str, Any]]

    identity_result: Optional[AgentResult]
    policy_result: Optional[AgentResult]
    fraud_result: Optional[AgentResult]

    agent_results: List[AgentResult]

    final_decision: Optional[str]      # APPROVED | REJECTED | HUMAN_REVIEW
    final_confidence: Optional[float]

    chat_history: List[Dict[str, str]]
    email_sent: bool

    # Optional path to an uploaded identity document image used by the identity agent
    identity_image_path: Optional[str]
    # Verified Aadhaar number from identity verification
    aadhaar_number: Optional[str]
    # Extracted Aadhaar holder name
    aadhaar_name: Optional[str]
    # Extracted Aadhaar holder age
    aadhaar_age: Optional[int]

    document_image_paths: list[str]
    document_name: Optional[str]
    document_age: Optional[int]
    document_summary: Optional[str]
    document_result: Optional[AgentResult]
    
    # Cross-agent validation data
    cross_agent_data: Optional[CrossAgentData]
    cross_validation_result: Optional[CrossValidationResult]
