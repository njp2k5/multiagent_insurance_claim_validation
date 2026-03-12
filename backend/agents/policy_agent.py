from typing import Optional, Dict, Any, cast
from datetime import date

from state import ClaimState, AgentResult
from db.session import SessionLocal
from models.policy import Policy
from policy.eligibility import evaluate_policy

def policy_agent(state: ClaimState) -> ClaimState:
    db = SessionLocal()

    # Resolve Aadhaar number from state (preferred) or from identity_result metadata
    aadhaar_no: Optional[str] = state.get("aadhaar_number")
    if not aadhaar_no:
        identity_result = state.get("identity_result") or {}
        metadata: Dict[str, Any] = identity_result.get("metadata", {}) if isinstance(identity_result, dict) else {}
        numbers = metadata.get("aadhaar_numbers") or []
        aadhaar_no = numbers[0] if numbers else None

    if not aadhaar_no:
        result: AgentResult = {
            "agent_name": "PolicyAgent",
            "status": "FAIL",
            "confidence": 0.3,
            "message": "Aadhaar number missing; cannot evaluate policy",
            "metadata": {"aadhaar_number": None}
        }
        state["policy_result"] = result
        agent_results = state.setdefault("agent_results", [])
        agent_results.append(result)
        return state

    claim = state.get("claim_form") or {}
    event = claim.get("event")
    amount_claimed = claim.get("amount_claimed")
    if event is None or amount_claimed is None:
        result: AgentResult = {
            "agent_name": "PolicyAgent",
            "status": "FAIL",
            "confidence": 0.3,
            "message": "Claim details incomplete; cannot evaluate policy",
            "metadata": {
                "aadhaar_number": aadhaar_no,
                "event": event,
                "amount_claimed": amount_claimed
            }
        }
        state["policy_result"] = result
        agent_results = state.setdefault("agent_results", [])
        agent_results.append(result)
        return state

    policy: Optional[Policy] = (
        db.query(Policy)
        .filter(Policy.aadhaar_no == aadhaar_no)
        .first()
    )

    if not policy:
        result: AgentResult = {
            "agent_name": "PolicyAgent",
            "status": "FAIL",
            "confidence": 0.3,
            "message": "No policy found for Aadhaar",
            "metadata": {
                "aadhaar_number": aadhaar_no,
                "current_plan": None
            }
        }
        state["policy_result"] = result
        agent_results = state.setdefault("agent_results", [])
        agent_results.append(result)
        return state

    plan_code = str(policy.policy_name)
    policy_expiry = cast(date, policy.policy_expiry)
    policy_start_date = cast(date, policy.policy_start) if hasattr(policy, 'policy_start') else None

    # Get claim type/event from state - supports new event categories
    claim_type = state.get("claim_type") or event  # Use claim_type if available, fallback to event

    eligible, message, coverage_details = evaluate_policy(
        plan_code=plan_code,
        policy_expiry=policy_expiry,
        event=claim_type,
        amount_claimed=amount_claimed,
        policy_start_date=policy_start_date
    )

    result: AgentResult = {
        "agent_name": "PolicyAgent",
        "status": "PASS" if eligible else "FAIL",
        "confidence": 0.85 if eligible else 0.3,
        "message": message,
        "metadata": {
            "aadhaar_number": aadhaar_no,
            "current_plan": plan_code,
            "plan_name": coverage_details.get("plan_name"),
            "event": claim_type,
            "amount_claimed": amount_claimed,
            "covered": coverage_details.get("covered", False),
            "max_amount": coverage_details.get("max_amount"),
            "co_pay_percent": coverage_details.get("co_pay_percent"),
            "claimable_amount": coverage_details.get("claimable_amount"),
            "coverage_details": coverage_details
        }
    }

    state["policy_result"] = result
    agent_results = state.setdefault("agent_results", [])
    agent_results.append(result)
    return state
