from fastapi import APIRouter
from state import ClaimState
from schemas.agent import AgentResponse

from agents.identity_agent import identity_verification_agent
from agents.document_agent import document_validation_agent
from agents.policy_agent import policy_agent
from agents.fraud_agent import fraud_detection_agent

router = APIRouter(prefix="/agents", tags=["Agents"])

@router.post("/identity", response_model=AgentResponse)
def identity(state: ClaimState):
    return identity_verification_agent(state)["identity_result"]

@router.post("/documents", response_model=AgentResponse)
def documents(state: ClaimState):
    return document_validation_agent(state)["document_result"]

@router.post("/policy", response_model=AgentResponse)
def policy(state: ClaimState):
    return policy_agent(state)["policy_result"]

@router.post("/fraud", response_model=AgentResponse)
def fraud(state: ClaimState):
    return fraud_detection_agent(state)["fraud_result"]
