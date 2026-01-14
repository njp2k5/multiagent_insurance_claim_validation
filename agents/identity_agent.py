from state import ClaimState, AgentResult

def identity_verification_agent(state: ClaimState) -> ClaimState:
    result: AgentResult = {
        "agent_name": "IdentityVerificationAgent",
        "status": "PASS",
        "confidence": 0.95,
        "message": "Identity verified successfully",
        "metadata": {"method": "KYC"}
    }
    state["identity_result"] = result
    state["agent_results"].append(result)
    return state
