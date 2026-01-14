from datetime import date
from typing import Optional, cast

from fastapi import APIRouter, Depends
from schemas.policy import PolicyCheckRequest
from policy.eligibility import evaluate_policy
from db.session import SessionLocal
from models.policy import Policy

router = APIRouter(prefix="/policy", tags=["Policy"])

@router.post("/check")
def check_policy(payload: PolicyCheckRequest):
    db = SessionLocal()
    
    # Fetch actual policy expiry from database
    policy: Optional[Policy] = (
        db.query(Policy)
        .filter(Policy.policy_name == payload.policy_plan_code)
        .first()
    )
    
    policy_expiry = cast(date, policy.policy_expiry) if policy else date.today()
    current_plan = str(policy.policy_name) if policy else None
    
    eligible, message = evaluate_policy(
        plan_code=payload.policy_plan_code,
        policy_expiry=policy_expiry,
        event=payload.test_claim.event,
        amount_claimed=payload.test_claim.amount_claimed
    )

    return {
        "agent_name": "PolicyAgent",
        "status": "PASS" if eligible else "FAIL",
        "current_plan": current_plan,
        "message": message
    }
