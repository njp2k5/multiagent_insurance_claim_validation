from pydantic import BaseModel
from typing import List, Dict

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    chat_history: List[Dict[str, str]]
