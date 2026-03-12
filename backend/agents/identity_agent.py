
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

    # Store the first verified Aadhaar number as the primary one
    primary_aadhaar = verified_numbers[0] if verified_numbers else None
    state["aadhaar_number"] = primary_aadhaar
    
    # Store extracted name and age
    aadhaar_name = result_data.get("aadhaar_name")
    aadhaar_age = result_data.get("aadhaar_age")
    state["aadhaar_name"] = aadhaar_name
    state["aadhaar_age"] = aadhaar_age
    
    # Populate cross_agent_data for cross-validation
    cross_agent_data = state.get("cross_agent_data", {})
    cross_agent_data["identity_name"] = aadhaar_name
    cross_agent_data["identity_age"] = aadhaar_age
    cross_agent_data["identity_aadhaar"] = primary_aadhaar
    state["cross_agent_data"] = cross_agent_data

    result: AgentResult = {
        "agent_name": "IdentityVerificationAgent",
        "status": status,
        "confidence": confidence,
        "message": "Identity verified successfully" if verified_numbers else "Aadhaar verification failed",
        "metadata": {
            "aadhaar_numbers": verified_numbers,
            "is_aadhaar": result_data["is_aadhaar"],
            "extracted_name": aadhaar_name,
            "extracted_age": aadhaar_age
        }
    }

    state["identity_result"] = result
    agent_results = state.setdefault("agent_results", [])
    agent_results.append(result)
    return state
