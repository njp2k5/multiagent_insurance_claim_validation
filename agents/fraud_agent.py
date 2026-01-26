from state import ClaimState, AgentResult, CrossValidationResult
from typing import List, Dict, Any
from difflib import SequenceMatcher


def normalize_name(name: str) -> str:
    """Normalize a name for comparison."""
    if not name:
        return ""
    # Convert to lowercase, remove extra spaces, and common prefixes
    name = name.lower().strip()
    # Remove common titles/prefixes
    for prefix in ["mr.", "mrs.", "ms.", "dr.", "shri", "smt.", "kumari"]:
        if name.startswith(prefix):
            name = name[len(prefix):].strip()
    # Remove extra spaces
    return " ".join(name.split())


def name_similarity(name1: str, name2: str) -> float:
    """Calculate similarity between two names (0.0 to 1.0)."""
    if not name1 or not name2:
        return 0.0
    n1 = normalize_name(name1)
    n2 = normalize_name(name2)
    return SequenceMatcher(None, n1, n2).ratio()


def cross_validate_agent_data(state: ClaimState) -> CrossValidationResult:
    """
    Cross-validate data extracted by different agents.
    Compares identity data with document data and claim form data.
    """
    cross_data = state.get("cross_agent_data", {})
    
    # Get names from different sources
    identity_name = cross_data.get("identity_name")
    document_name = cross_data.get("document_name")
    claim_form = state.get("claim_form", {})
    claim_form_name = claim_form.get("claimant_name") or claim_form.get("name")
    
    # Get ages from different sources
    identity_age = cross_data.get("identity_age")
    document_age = cross_data.get("document_age")
    claim_form_age = claim_form.get("age")
    
    # Store claim form data in cross_agent_data
    if claim_form_name:
        cross_data["claim_form_name"] = claim_form_name
    if claim_form_age:
        cross_data["claim_form_age"] = claim_form_age
    state["cross_agent_data"] = cross_data
    
    inconsistencies: List[Dict[str, Any]] = []
    name_match = True
    age_match = True
    
    # Collect available names and ages for comparison
    names = {
        "identity": identity_name,
        "document": document_name,
        "claim_form": claim_form_name
    }
    ages = {
        "identity": identity_age,
        "document": document_age,
        "claim_form": claim_form_age
    }
    
    # Filter out None values
    available_names = {k: v for k, v in names.items() if v}
    available_ages = {k: v for k, v in ages.items() if v}
    
    # Check if we have enough data
    if len(available_names) < 2 and len(available_ages) < 2:
        return {
            "status": "INSUFFICIENT_DATA",
            "name_match": False,
            "age_match": False,
            "inconsistencies": [],
            "confidence": 0.0,
            "message": "Not enough data from different agents to perform cross-validation"
        }
    
    # Cross-validate names
    name_threshold = 0.75  # 75% similarity threshold
    name_sources = list(available_names.keys())
    for i in range(len(name_sources)):
        for j in range(i + 1, len(name_sources)):
            source1, source2 = name_sources[i], name_sources[j]
            name1, name2 = available_names[source1], available_names[source2]
            similarity = name_similarity(name1, name2)
            
            if similarity < name_threshold:
                name_match = False
                inconsistencies.append({
                    "field": "name",
                    "source1": source1,
                    "value1": name1,
                    "source2": source2,
                    "value2": name2,
                    "similarity": round(similarity, 2),
                    "threshold": name_threshold
                })
    
    # Cross-validate ages (exact match required, with ±1 year tolerance)
    age_sources = list(available_ages.keys())
    for i in range(len(age_sources)):
        for j in range(i + 1, len(age_sources)):
            source1, source2 = age_sources[i], age_sources[j]
            age1, age2 = available_ages[source1], available_ages[source2]
            
            if abs(age1 - age2) > 1:  # Allow 1 year tolerance
                age_match = False
                inconsistencies.append({
                    "field": "age",
                    "source1": source1,
                    "value1": age1,
                    "source2": source2,
                    "value2": age2,
                    "difference": abs(age1 - age2)
                })
    
    # Determine overall status
    if name_match and age_match:
        status = "VERIFIED"
        confidence = 0.95
        message = "All cross-agent data matches successfully"
    elif name_match or age_match:
        status = "PARTIAL_MATCH"
        confidence = 0.6
        mismatched = []
        if not name_match:
            mismatched.append("name")
        if not age_match:
            mismatched.append("age")
        message = f"Partial match - inconsistencies found in: {', '.join(mismatched)}"
    else:
        status = "MISMATCH"
        confidence = 0.3
        message = "Cross-validation failed - multiple inconsistencies detected"
    
    return {
        "status": status,
        "name_match": name_match,
        "age_match": age_match,
        "inconsistencies": inconsistencies,
        "confidence": confidence,
        "message": message
    }


def fraud_detection_agent(state: ClaimState) -> ClaimState:
    claim_form = state.get("claim_form")
    if not claim_form:
        amount = 0
    else:
        amount = claim_form.get("amount", 0)
    suspicious = amount > 300000
    
    # Perform cross-validation
    cross_validation_result = cross_validate_agent_data(state)
    state["cross_validation_result"] = cross_validation_result
    
    # Factor in cross-validation results for fraud detection
    cross_validation_suspicious = cross_validation_result["status"] == "MISMATCH"
    
    # Determine overall fraud status
    if suspicious and cross_validation_suspicious:
        status = "FLAG"
        confidence = 0.85
        message = "High fraud risk - suspicious amount and identity mismatch detected"
        risk_score = 0.9
    elif cross_validation_suspicious:
        status = "FLAG"
        confidence = 0.75
        message = "Potential fraud - identity/document mismatch detected"
        risk_score = 0.72
    elif suspicious:
        status = "FLAG"
        confidence = 0.6
        message = "Potential fraud detected - high claim amount"
        risk_score = 0.6
    elif cross_validation_result["status"] == "PARTIAL_MATCH":
        status = "FLAG"
        confidence = 0.5
        message = "Minor discrepancies detected in claimant information"
        risk_score = 0.4
    else:
        status = "PASS"
        confidence = 0.9
        message = "No fraud risk - all validations passed"
        risk_score = 0.1

    result: AgentResult = {
        "agent_name": "FraudDetectionAgent",
        "status": status,
        "confidence": confidence,
        "message": message,
        "metadata": {
            "risk_score": risk_score,
            "amount_suspicious": suspicious,
            "cross_validation_status": cross_validation_result["status"],
            "cross_validation_details": cross_validation_result
        }
    }

    state["fraud_result"] = result
    if "agent_results" not in state:
        state["agent_results"] = []
    state["agent_results"].append(result)
    return state
