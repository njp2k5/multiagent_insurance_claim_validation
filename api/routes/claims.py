from fastapi import APIRouter
from graph.claim_graph import build_claim_graph
from state import ClaimState
from schemas.decision import FinalDecisionResponse

router = APIRouter(prefix="/claims", tags=["Claims"])

@router.post("/process", response_model=FinalDecisionResponse)
def process_claim(state: ClaimState):
    try:
        # Ensure required fields are initialized
        if "agent_results" not in state or state["agent_results"] is None:
            state["agent_results"] = []
        if "chat_history" not in state or state["chat_history"] is None:
            state["chat_history"] = []
        if "email_sent" not in state:
            state["email_sent"] = False
        
        graph = build_claim_graph()
        final_state = graph.invoke(state)
        return {
            "claim_id": final_state.get("claim_id"),
            "final_decision": final_state.get("final_decision"),
            "final_confidence": final_state.get("final_confidence"),
            "agent_results": final_state.get("agent_results", [])
        }
    except Exception as e:
        print(f"Error processing claim: {e}")
        raise
