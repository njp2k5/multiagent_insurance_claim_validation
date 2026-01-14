from state import ClaimState, AgentResult

def policy_agent(state: ClaimState) -> ClaimState:
    claim_form = state.get("claim_form")
    if not claim_form:
        amount = 0
    else:
        amount = claim_form.get("amount", 0)
    eligible = amount <= 500000

    result: AgentResult = {
        "agent_name": "PolicyAgent",
        "status": "PASS" if eligible else "FAIL",
        "confidence": 0.85 if eligible else 0.3,
        "message": "Policy eligible" if eligible else "Policy limit exceeded",
        "metadata": {"amount": amount}
    }

    state["policy_result"] = result
    state["agent_results"].append(result)
    return state
