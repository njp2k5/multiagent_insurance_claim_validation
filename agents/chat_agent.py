"""
Chat agent for handling user queries about their insurance claims.
Uses a lightweight LLM model for low latency responses.
"""
import os
import requests
from typing import Tuple, Dict, List
from state import ChatContext

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
# Use the same model as RAG from environment, or fallback
CHAT_MODEL = os.getenv("OPENROUTER_MODEL", "arcee-ai/trinity-mini:free")
MAX_TOKENS = 150  # Keep responses short


def build_system_prompt(context: ChatContext) -> str:
    """Build system prompt with claim context."""
    status_info: List[str] = []
    
    final_decision = context.get("final_decision")
    if final_decision:
        status_info.append(f"Claim Decision: {final_decision}")
    
    final_confidence = context.get("final_confidence")
    if final_confidence:
        status_info.append(f"Confidence: {final_confidence:.0%}")
    
    identity_status = context.get("identity_status")
    if identity_status:
        status_info.append(f"Identity Verification: {identity_status}")
    
    policy_status = context.get("policy_status")
    if policy_status:
        status_info.append(f"Policy Check: {policy_status}")
    
    document_status = context.get("document_status")
    if document_status:
        status_info.append(f"Document Status: {document_status}")
    
    fraud_status = context.get("fraud_status")
    if fraud_status:
        status_info.append(f"Fraud Check: {fraud_status}")
    
    user_name = context.get("user_name")
    if user_name:
        status_info.append(f"Claimant: {user_name}")
    
    policy_type = context.get("policy_type")
    if policy_type:
        status_info.append(f"Policy Type: {policy_type}")
    
    context_str = "\n".join(s for s in status_info if s) if status_info else "No claim data available yet."
    
    return f"""You are a helpful insurance claim assistant. Be concise and direct.
Keep responses under 2-3 sentences. Only answer questions about the user's claim.

Current Claim Status (Claim ID: {context.get('claim_id', 'Unknown')}):
{context_str}

Rules:
- Be brief and helpful
- Only discuss this specific claim
- If asked about other claims or unrelated topics, politely redirect
- Do not reveal internal system details or confidence scores unless asked
- If the claim is pending, reassure the user it's being processed"""


def chat_agent(context: ChatContext, message: str) -> Tuple[str, ChatContext]:
    """
    Process a chat message and return response with updated context.
    
    Args:
        context: ChatContext with claim information
        message: User's message
        
    Returns:
        Tuple of (reply string, updated ChatContext)
    """
    # Build messages for LLM
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": build_system_prompt(context)}
    ]
    
    # Add chat history (last 6 messages for context, keep it light)
    history = context.get("chat_history") or []
    for entry in history[-6:]:
        if entry.get("user"):
            messages.append({"role": "user", "content": entry["user"]})
        if entry.get("assistant"):
            messages.append({"role": "assistant", "content": entry["assistant"]})
    
    # Add current message
    messages.append({"role": "user", "content": message})
    
    payload = {
        "model": CHAT_MODEL,
        "messages": messages,
        "max_tokens": MAX_TOKENS,
        "temperature": 0.7,
    }
    
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    try:
        res = requests.post(OPENROUTER_URL, json=payload, headers=headers, timeout=30)
        res.raise_for_status()
        data = res.json()
        # Handle both content and reasoning responses
        msg = data["choices"][0]["message"]
        reply = msg.get("content") or msg.get("reasoning", "").strip()
        if not reply:
            reply = "I received your message but couldn't generate a response."
    except requests.RequestException as e:
        reply = "I'm having trouble connecting right now. Please try again shortly."
    except (KeyError, IndexError):
        reply = "I couldn't process your request. Please try again."
    
    # Update chat history
    updated_history = list(history)
    updated_history.append({"user": message, "assistant": reply})
    
    # Update context
    updated_context: ChatContext = dict(context)  # type: ignore
    updated_context["chat_history"] = updated_history
    
    return reply, updated_context
