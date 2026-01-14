from state import ClaimState

def send_decision_email(state: ClaimState) -> ClaimState:
    print(f"""
    EMAIL TO: {state['user_email']}
    DECISION: {state['final_decision']}
    CONFIDENCE: {state['final_confidence']}
    """)
    state["email_sent"] = True
    return state
