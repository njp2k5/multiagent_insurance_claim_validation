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
    
    # Claimant type: 'user' or 'company'
    claimant_type: Optional[str]
    # Type of claim: e.g., 'health', 'vehicle', 'property', 'life', etc.
    claim_type: Optional[str]

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


class ChatContext(TypedDict, total=False):
    """Lightweight state for chat agent - contains only relevant claim info."""
    claim_id: str
    claim_status: Optional[str]  # Current claim status
    final_decision: Optional[str]  # APPROVED | REJECTED | HUMAN_REVIEW
    final_confidence: Optional[float]
    
    # Brief summaries from agents
    identity_status: Optional[str]
    policy_status: Optional[str]
    fraud_status: Optional[str]
    document_status: Optional[str]
    
    # User info
    user_name: Optional[str]
    policy_type: Optional[str]
    
    # Chat history for context
    chat_history: List[Dict[str, str]]
    
    # Validation tracking
    chat_session_validated: bool


def extract_chat_context(state: ClaimState) -> ChatContext:
    """Extract minimal context from ClaimState for chat agent."""
    context: ChatContext = {
        "claim_id": state.get("claim_id") or "",
        "final_decision": state.get("final_decision"),
        "final_confidence": state.get("final_confidence"),
        "chat_history": state.get("chat_history") or [],
        "chat_session_validated": False,
    }
    
    # Extract agent statuses safely
    identity_result = state.get("identity_result")
    if identity_result:
        context["identity_status"] = identity_result.get("status")
    
    policy_result = state.get("policy_result")
    if policy_result:
        context["policy_status"] = policy_result.get("status")
    
    fraud_result = state.get("fraud_result")
    if fraud_result:
        context["fraud_status"] = fraud_result.get("status")
    
    document_result = state.get("document_result")
    if document_result:
        context["document_status"] = document_result.get("status")
    
    # Extract user info
    context["user_name"] = state.get("aadhaar_name") or state.get("document_name")
    claim_form = state.get("claim_form")
    if claim_form:
        context["policy_type"] = claim_form.get("policy_type")
    
    return context
