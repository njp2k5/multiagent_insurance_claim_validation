from state import ClaimState

def chat_agent(state: ClaimState, message: str) -> ClaimState:
    reply = f"I understand your question: '{message}'. Your claim is being processed."
    state["chat_history"].append({"user": message, "assistant": reply})
    return state
