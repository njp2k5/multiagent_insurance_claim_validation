"""
Chat endpoint for claim-related queries.
Provides one-time claim ID validation and chat functionality.
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict
import secrets
import time

from schemas.chat import ChatInitRequest, ChatInitResponse, ChatRequest, ChatResponse
from services.claim_store import claim_store
from state import extract_chat_context, ChatContext
from agents.chat_agent import chat_agent

router = APIRouter(prefix="/chat", tags=["Chat"])

# In-memory session store (use Redis in production)
# Maps session_token -> {claim_id, context, created_at, validated}
_chat_sessions: Dict[str, Dict] = {}

# Session expiry in seconds (30 minutes)
SESSION_EXPIRY = 1800


def _cleanup_expired_sessions():
    """Remove expired sessions."""
    now = time.time()
    expired = [k for k, v in _chat_sessions.items() if now - v["created_at"] > SESSION_EXPIRY]
    for k in expired:
        del _chat_sessions[k]


@router.post("/init", response_model=ChatInitResponse)
def init_chat_session(request: ChatInitRequest):
    """
    Initialize a chat session with one-time claim ID validation.
    Returns a session token for subsequent chat requests.
    """
    _cleanup_expired_sessions()
    
    # Validate claim exists
    claim_state = claim_store.get_claim(request.claim_id)
    if not claim_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found. Please check your claim ID."
        )
    
    # Extract chat context from claim state
    chat_context = extract_chat_context(claim_state)
    chat_context["chat_session_validated"] = True
    
    # Generate session token
    session_token = secrets.token_urlsafe(32)
    
    # Store session
    _chat_sessions[session_token] = {
        "claim_id": request.claim_id,
        "context": chat_context,
        "created_at": time.time(),
        "validated": True
    }
    
    return ChatInitResponse(
        session_token=session_token,
        claim_id=request.claim_id,
        message="Chat session initialized. You can now ask questions about your claim."
    )


@router.post("/message", response_model=ChatResponse)
def send_message(request: ChatRequest):
    """
    Send a chat message. Requires a valid session token from /chat/init.
    """
    _cleanup_expired_sessions()
    
    # Validate session
    session = _chat_sessions.get(request.session_token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session. Please initialize a new chat session."
        )
    
    # Check session expiry
    if time.time() - session["created_at"] > SESSION_EXPIRY:
        del _chat_sessions[request.session_token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please initialize a new chat session."
        )
    
    # Get context and process message
    context: ChatContext = session["context"]
    
    # Call chat agent
    reply, updated_context = chat_agent(context, request.message)
    
    # Update session context
    session["context"] = updated_context
    
    # Also update the main claim store with chat history
    claim_state = claim_store.get_claim(session["claim_id"])
    if claim_state:
        claim_state["chat_history"] = updated_context.get("chat_history", [])
        claim_store.update_claim(session["claim_id"], claim_state)
    
    return ChatResponse(
        reply=reply,
        chat_history=updated_context.get("chat_history", []),
        claim_id=session["claim_id"]
    )


@router.get("/history/{session_token}")
def get_chat_history(session_token: str):
    """Get chat history for a session."""
    session = _chat_sessions.get(session_token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found."
        )
    
    return {
        "claim_id": session["claim_id"],
        "chat_history": session["context"].get("chat_history", [])
    }
