from fastapi import APIRouter, HTTPException
from typing import cast, Dict, Any
from state import ClaimState
from schemas.agent import (
    CrossValidationResponse,
    InconsistencyDetail
)
from services.claim_store import claim_store
from agents.fraud_agent import cross_validate_agent_data

router = APIRouter(prefix="/fraud", tags=["Fraud Detection"])


@router.get("/cross-validate/{claim_id}", response_model=CrossValidationResponse)
def cross_validate_claim(claim_id: str):
    """
    Cross-validate data from different agents (identity, document, claim form)
    for a specific claim. Returns VERIFIED if all data matches, or details 
    about inconsistencies.
    
    This endpoint reads the state that has been updated by individual agents
    (identity agent, document agent) and performs cross-validation.
    """
    # Get the claim state from store
    state = claim_store.get_claim(claim_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")
    
    # Perform cross-validation on the stored state
    result = cast(Dict[str, Any], cross_validate_agent_data(state))
    
    # Update the state with cross-validation result (cast to satisfy TypedDict)
    state["cross_validation_result"] = cast(Any, result)
    claim_store.update_claim(claim_id, state)
    
    # Get cross_agent_data for response
    cross_data = cast(Dict[str, Any], state.get("cross_agent_data") or {})
    
    # Convert inconsistencies to proper format
    inconsistencies = [
        InconsistencyDetail(**inc) for inc in result.get("inconsistencies", [])
    ]
    
    return CrossValidationResponse(
        status=result.get("status", "INSUFFICIENT_DATA"),
        name_match=result.get("name_match", False),
        age_match=result.get("age_match", False),
        inconsistencies=inconsistencies,
        confidence=result.get("confidence", 0.0),
        message=result.get("message", "")
    )
