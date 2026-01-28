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
    claim_id: Optional[str] = Query(None, description="Specific claim ID to send report for. If not provided, sends report for the latest claim."),
    current_user: User = Depends(get_current_user)
):
    """
    Master Agent endpoint that:
    1. Combines and analyzes results from all agents (Identity, Policy, Document, Fraud)
    2. Makes a final decision on the claim
    3. Drafts a customized email with all agent findings
    4. Sends the email to the authenticated user's email address
    
    The email includes:
    - Final claim decision (APPROVED/REJECTED/HUMAN_REVIEW)
    - Identity verification results
    - Policy eligibility check results
    - Document analysis summary
    - Cross-validation findings
    - Fraud detection analysis
    - Next steps based on decision
    """
    user_email = current_user.username  # username is the email
    
    # Get the claim state
    if claim_id:
        state = claim_store.get_claim(claim_id)
        if not state:
            raise HTTPException(
                status_code=404, 
                detail=f"Claim with ID '{claim_id}' not found"
            )
    else:
        # Get the latest claim for this user or any claim if user filter not available
        all_claims = claim_store.list_claims()
        if not all_claims:
            raise HTTPException(
                status_code=404,
                detail="No claims found. Please submit a claim first."
            )
        
        # Try to find a claim for this user, or get the most recent one
        user_claims = [
            (cid, state) for cid, state in all_claims.items()
            if state.get("user_email") == user_email or state.get("user_id") == user_email
        ]
        
        if user_claims:
            claim_id, state = user_claims[-1]  # Get the latest user claim
        else:
            # Fall back to the last claim in the store
            claim_id, state = list(all_claims.items())[-1]
    
    # Check if there are any agent results to process
    if not state.get("agent_results"):
        raise HTTPException(
            status_code=400,
            detail="No agent results found for this claim. Please complete the verification steps first."
        )
    
    # Run master agent to send report
    result = master_agent_send_report(str(user_email), state)
    
    # Update the claim state in store
    claim_store.update_claim(claim_id, result["state"])
    
    if not result["email_result"].get("success"):
        raise HTTPException(
            status_code=500,
            detail=result["email_result"].get("error", "Failed to send email")
        )
    
    return {
        "message": "Claim report email sent successfully",
        "recipient": user_email,
        "claim_id": claim_id,
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
    user_email = current_user.username
    
    if claim_id:
        state = claim_store.get_claim(claim_id)
        if not state:
            raise HTTPException(
                status_code=404,
                detail=f"Claim with ID '{claim_id}' not found"
            )
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
    
    user_email = current_user.username
    
    if claim_id:
        state = claim_store.get_claim(claim_id)
        if not state:
            raise HTTPException(
                status_code=404,
                detail=f"Claim with ID '{claim_id}' not found"
            )
    else:
        all_claims = claim_store.list_claims()
        if not all_claims:
            raise HTTPException(
                status_code=404,
                detail="No claims found."
            )
        claim_id, state = list(all_claims.items())[-1]
    
    if not state.get("final_decision") and state.get("agent_results"):
        state = master_decision_agent(state)
        claim_store.update_claim(claim_id, state)
    
    summary = get_agent_summary(state)
    html_content = draft_claim_email(str(user_email), summary)
    
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content)
