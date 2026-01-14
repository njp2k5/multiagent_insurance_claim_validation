
from state import ClaimState, AgentResult
from identity.classifier import AadhaarClassifier

def identity_verification_agent(state: ClaimState) -> ClaimState:
    classifier = AadhaarClassifier()
    image_path = state.get("identity_image_path")
    if not image_path:
        raise ValueError("identity_image_path is required for identity verification")

    result_data = classifier.classify(image_path)

    verified_numbers = [k for k, v in result_data["verified"].items() if v]

    status = "PASS" if verified_numbers else "FAIL"
    confidence = 0.95 if verified_numbers else 0.3

    result: AgentResult = {
        "agent_name": "IdentityVerificationAgent",
        "status": status,
        "confidence": confidence,
        "message": "Identity verified successfully" if verified_numbers else "Aadhaar verification failed",
        "metadata": {
            "aadhaar_numbers": verified_numbers,
            "is_aadhaar": result_data["is_aadhaar"]
        }
    }

    state["identity_result"] = result
    agent_results = state.setdefault("agent_results", [])
    agent_results.append(result)
    return state
