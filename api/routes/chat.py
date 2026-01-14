from fastapi import APIRouter
from schemas.chat import ChatRequest, ChatResponse
from agents.chat_agent import chat_agent
from state import ClaimState

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/message", response_model=ChatResponse)
def chat(state: ClaimState, payload: ChatRequest):
    updated = chat_agent(state, payload.message)
    return {
        "reply": updated["chat_history"][-1]["assistant"],
        "chat_history": updated["chat_history"]
    }
