from state import ClaimState, AgentResult

def fraud_detection_agent(state: ClaimState) -> ClaimState:
    claim_form = state.get("claim_form")
    if not claim_form:
        amount = 0
    else:
        amount = claim_form.get("amount", 0)
    suspicious = amount > 300000

    result: AgentResult = {
        "agent_name": "FraudDetectionAgent",
        "status": "FLAG" if suspicious else "PASS",
        "confidence": 0.6 if suspicious else 0.9,
        "message": "Potential fraud detected" if suspicious else "No fraud risk",
        "metadata": {"risk_score": 0.72 if suspicious else 0.1}
    }

    state["fraud_result"] = result
    state["agent_results"].append(result)
    return state
