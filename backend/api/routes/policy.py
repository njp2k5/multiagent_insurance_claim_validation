from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from db.session import SessionLocal
from models.policy import Policy
from services.claim_store import claim_store

router = APIRouter(prefix="/policy", tags=["Policy"])

def _resolve_aadhaar_from_state(state) -> Optional[str]:
    # Prefer direct field
    aadhaar_no = state.get("aadhaar_number")
    if aadhaar_no:
        return aadhaar_no

    # Fallback to identity_result metadata list
    identity_result = state.get("identity_result") or {}
    metadata = identity_result.get("metadata") or {}
    numbers = metadata.get("aadhaar_numbers") or []
    if numbers:
        return numbers[0]
    return None


@router.get("/check")
def check_policy(claim_id: str = Query(..., description="Claim ID whose Aadhaar should be checked")):
    state = claim_store.get_claim(claim_id)
    if not state:
        raise HTTPException(status_code=404, detail="Claim not found")

    aadhaar_no = _resolve_aadhaar_from_state(state)
    if not aadhaar_no:
        raise HTTPException(status_code=400, detail="Aadhaar number not available in claim state")

    with SessionLocal() as db:
        policy: Optional[Policy] = (
            db.query(Policy)
            .filter(Policy.aadhaar_no == aadhaar_no)
            .first()
        )

    if not policy:
        result = {
            "agent_name": "PolicyAgent",
            "status": "FAIL",
            "confidence": 0.3,
            "message": "No policy found for Aadhaar",
            "metadata": {
                "aadhaar_number": aadhaar_no,
                "current_plan": None,
                "policy_expiry": None,
            },
        }
        # Update state even on failure
        state["policy_result"] = result
        agent_results = state.setdefault("agent_results", [])
        agent_results.append(result)
        claim_store.update_claim(claim_id, state)
    else:
        policy_name = str(policy.policy_name)
        policy_expiry = policy.policy_expiry.isoformat() if isinstance(policy.policy_expiry, date) else None
        result = {
            "agent_name": "PolicyAgent",
            "status": "PASS",
            "confidence": 0.85,
            "message": "Policy found for Aadhaar",
            "metadata": {
                "aadhaar_number": aadhaar_no,
                "current_plan": policy_name,
                "policy_expiry": policy_expiry,
            },
        }
        # Update state with policy info for downstream use
        state["policy_result"] = result
        agent_results = state.setdefault("agent_results", [])
        agent_results.append(result)
        claim_store.update_claim(claim_id, state)

    return {
        "agent_name": result["agent_name"],
        "status": result["status"],
        "policy_name": result["metadata"].get("current_plan"),
        "policy_expiry": result["metadata"].get("policy_expiry"),
        "aadhaar_number": aadhaar_no,
        "message": result["message"],
    }
