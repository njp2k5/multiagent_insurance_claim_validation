from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from db.session import SessionLocal
from models.user import User
from auth.oauth2 import oauth2_scheme
from auth.jwt_handler import decode_access_token
from services.claim_store import claim_store
from agents.master_agent import (
    master_decision_agent,
    get_agent_summary,
    send_claim_email,
    master_agent_send_report
)

router = APIRouter(prefix="/master", tags=["Master Agent"])


@router.get("/debug-claim/{claim_id}")
def debug_claim_state(claim_id: str):
    """
    Debug endpoint to view the current claim state.
    Useful for troubleshooting what data has been collected by agents.
    """
    state = claim_store.get_claim(claim_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")
    
    # Return a sanitized view of the state
    return {
        "claim_id": state.get("claim_id"),
        "user_email": state.get("user_email"),
        "claim_type": state.get("claim_type"),
        "claimant_type": state.get("claimant_type"),
        "identity_result": state.get("identity_result"),
        "policy_result": state.get("policy_result"),
        "document_result": state.get("document_result"),
        "fraud_result": state.get("fraud_result"),
        "cross_validation_result": state.get("cross_validation_result"),
        "agent_results_count": len(state.get("agent_results", [])),
        "agent_names": [r.get("agent_name") for r in state.get("agent_results", [])],
        "final_decision": state.get("final_decision"),
        "final_confidence": state.get("final_confidence"),
        "aadhaar_name": state.get("aadhaar_name"),
        "aadhaar_number": state.get("aadhaar_number"),
        "document_name": state.get("document_name"),
        "document_summary": state.get("document_summary"),
        "cross_agent_data": state.get("cross_agent_data"),
    }


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get the currently authenticated user."""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.get("/send-report")
def send_claim_report(
    claim_id: str = Query(..., description="Required claim ID to send report for."),
    user_email: Optional[str] = Query(None, description="Optional email to use if claim state is missing user_email.")
):
    """
    Master Agent endpoint that:
    1. Combines and analyzes results from all agents (Identity, Policy, Document, Fraud)
    2. Makes a final decision on the claim
    3. Drafts a customized email with all agent findings
    4. Sends the email to the user's email address from the claim state
    
    The email includes:
    - Final claim decision (APPROVED/REJECTED/HUMAN_REVIEW)
    - Identity verification results
    - Policy eligibility check results
    - Document analysis summary
    - Cross-validation findings
    - Fraud detection analysis
    - Next steps based on decision
    """
    # Get the claim state
    state = claim_store.get_claim(claim_id)
    if not state:
        raise HTTPException(
            status_code=404, 
            detail=f"Claim with ID '{claim_id}' not found"
        )
    
    # Get user email from claim state or query param
    state_user_email = state.get("user_email")
    resolved_user_email = state_user_email or user_email
    if not resolved_user_email:
        raise HTTPException(
            status_code=400,
            detail="User email not found in claim state. Provide user_email query parameter."
        )
    if not state_user_email and user_email:
        state["user_email"] = str(user_email)
        claim_store.update_claim(claim_id, state)
    
    # Initialize agent_results if missing to allow sending report with available data
    if not state.get("agent_results"):
        state["agent_results"] = []
    
    # Run master agent to send report
    result = master_agent_send_report(str(resolved_user_email), state)
    
    # Update the claim state in store
    claim_store.update_claim(claim_id, result["state"])
    
    if not result["email_result"].get("success"):
        raise HTTPException(
            status_code=500,
            detail=result["email_result"].get("error", "Failed to send email")
        )
    
    return {
        "message": "Claim report email sent successfully",
        "recipient": resolved_user_email,
        "claim_id": claim_id,
        # Convenience link for front-end or email templates: includes claim_id as query parameter
        "send_report_link": f"/master/send-report?claim_id={claim_id}",
        "decision": result["summary"].get("final_decision"),
        "confidence": result["summary"].get("final_confidence"),
        "email_sent": True
    }


@router.get("/claim-summary")
def get_claim_summary(
    claim_id: Optional[str] = Query(None, description="Specific claim ID to get summary for."),
    current_user: User = Depends(get_current_user)
):
    """
    Get a comprehensive summary of all agent findings for a claim without sending an email.
    Useful for reviewing claim status before sending the final report.
    """
    user_email = str(current_user.username)
    
    if claim_id:
        state = claim_store.get_claim(claim_id)
        if not state:
            raise HTTPException(
                status_code=404,
                detail=f"Claim with ID '{claim_id}' not found"
            )
        # Update user_email in claim state
        state["user_email"] = str(user_email)
        claim_store.update_claim(claim_id, state)
    else:
        all_claims = claim_store.list_claims()
        if not all_claims:
            raise HTTPException(
                status_code=404,
                detail="No claims found."
            )
        
        user_claims = [
            (cid, state) for cid, state in all_claims.items()
            if state.get("user_email") == user_email or state.get("user_id") == user_email
        ]
        
        if user_claims:
            claim_id, state = user_claims[-1]
        else:
            claim_id, state = list(all_claims.items())[-1]
        
        # Update user_email in claim state
        state["user_email"] = str(user_email)
        claim_store.update_claim(claim_id, state)
    
    # Run decision if not already done
    if not state.get("final_decision") and state.get("agent_results"):
        state = master_decision_agent(state)
        claim_store.update_claim(claim_id, state)
    
    summary = get_agent_summary(state)
    
    return {
        "claim_id": claim_id,
        "summary": summary,
        "email_sent": state.get("email_sent", False)
    }


@router.get("/preview-email")
def preview_email(
    claim_id: Optional[str] = Query(None, description="Specific claim ID to preview email for."),
    current_user: User = Depends(get_current_user)
):
    """
    Preview the email that would be sent without actually sending it.
    Returns the HTML content of the email for review.
    """
    from agents.master_agent import draft_claim_email
    
    user_email = str(current_user.username)
    
    if claim_id:
        state = claim_store.get_claim(claim_id)
        if not state:
            raise HTTPException(
                status_code=404,
                detail=f"Claim with ID '{claim_id}' not found"
            )
        # Update user_email in claim state
        state["user_email"] = str(user_email)
        claim_store.update_claim(claim_id, state)
    else:
        all_claims = claim_store.list_claims()
        if not all_claims:
            raise HTTPException(
                status_code=404,
                detail="No claims found."
            )
        claim_id, state = list(all_claims.items())[-1]
        # Update user_email in claim state
        state["user_email"] = str(user_email)
        claim_store.update_claim(claim_id, state)
    
    if not state.get("final_decision") and state.get("agent_results"):
        state = master_decision_agent(state)
        claim_store.update_claim(claim_id, state)
    
    summary = get_agent_summary(state)
    html_content = draft_claim_email(str(user_email), summary)
    
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content)
