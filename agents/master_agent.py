from state import ClaimState

def master_decision_agent(state: ClaimState) -> ClaimState:
    results = state["agent_results"]
    avg_conf = sum(r["confidence"] for r in results) / len(results)

    if any(r["status"] == "FAIL" for r in results):
        decision = "REJECTED"
    elif any(r["status"] == "FLAG" for r in results) or avg_conf < 0.7:
        decision = "HUMAN_REVIEW"
    else:
        decision = "APPROVED"

    state["final_decision"] = decision
    state["final_confidence"] = round(avg_conf, 2)
    return state
