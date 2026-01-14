from langgraph.graph import StateGraph, END
from state import ClaimState

from agents.identity_agent import identity_verification_agent
from agents.document_agent import document_validation_agent
from agents.policy_agent import policy_agent
from agents.fraud_agent import fraud_detection_agent
from agents.master_agent import master_decision_agent
from services.notifications import send_decision_email

def build_claim_graph():
    graph = StateGraph(ClaimState)

    graph.add_node("identity", identity_verification_agent)
    graph.add_node("documents", document_validation_agent)
    graph.add_node("policy", policy_agent)
    graph.add_node("fraud", fraud_detection_agent)
    graph.add_node("decision", master_decision_agent)
    graph.add_node("notify", send_decision_email)

    graph.set_entry_point("identity")

    graph.add_edge("identity", "documents")
    graph.add_edge("identity", "policy")
    graph.add_edge("identity", "fraud")

    graph.add_edge("documents", "decision")
    graph.add_edge("policy", "decision")
    graph.add_edge("fraud", "decision")

    graph.add_edge("decision", "notify")
    graph.add_edge("notify", END)

    return graph.compile()
