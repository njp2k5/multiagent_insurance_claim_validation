from typing import TypedDict, List, Dict, Any, Optional


class AgentResult(TypedDict):
    agent_name: str
    status: str        # PASS | FAIL | FLAG | INFO
    confidence: float
    message: str
    metadata: Dict[str, Any]


class ClaimState(TypedDict, total=False):
    user_id: str
    user_email: str
    is_authenticated: bool

    claim_id: Optional[str]
    claim_form: Optional[Dict[str, Any]]
    documents: Optional[List[str]]

    identity_result: Optional[AgentResult]
    document_result: Optional[AgentResult]
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
