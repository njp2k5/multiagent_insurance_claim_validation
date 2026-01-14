from state import ClaimState, AgentResult

REQUIRED_DOCS = {"ID_PROOF", "POLICY_DOC", "CLAIM_FORM"}

def document_validation_agent(state: ClaimState) -> ClaimState:
    uploaded = set(state.get("documents") or [])
    missing = REQUIRED_DOCS - uploaded

    if missing:
        result: AgentResult = {
            "agent_name": "DocumentValidationAgent",
            "status": "FAIL",
            "confidence": 0.4,
            "message": "Missing documents",
            "metadata": {"missing": list(missing)}
        }
    else:
        result: AgentResult = {
            "agent_name": "DocumentValidationAgent",
            "status": "PASS",
            "confidence": 0.9,
            "message": "All documents valid",
            "metadata": {}
        }

    state["document_result"] = result
    state["agent_results"].append(result)
    return state
