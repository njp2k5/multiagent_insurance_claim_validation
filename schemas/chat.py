from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class ChatInitRequest(BaseModel):
    """One-time claim ID validation to start chat session."""
    claim_id: str = Field(..., description="Claim ID to validate and start chat session")


class ChatInitResponse(BaseModel):
    """Response for chat session initialization."""
    session_token: str
    claim_id: str
    message: str


class ChatRequest(BaseModel):
    """Chat message request."""
    message: str = Field(..., max_length=500, description="User message (max 500 chars)")
    session_token: str = Field(..., description="Session token from chat init")


class ChatResponse(BaseModel):
    """Chat response with history."""
    reply: str
    chat_history: List[Dict[str, str]]
    claim_id: Optional[str] = None
