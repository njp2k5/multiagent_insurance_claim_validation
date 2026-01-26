from fastapi import APIRouter, UploadFile, File, HTTPException, Query
import uuid, os
from typing import Optional

from identity.classifier import AadhaarClassifier
from agents.identity_agent import identity_verification_agent
from state import ClaimState
from services.claim_store import claim_store

router = APIRouter(prefix="/identity", tags=["Identity"])

UPLOAD_DIR = "uploads/identity"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/create-claim")
def create_claim():
    """Create a new claim and return the claim ID."""
    claim_id = claim_store.create_claim()
    return {"claim_id": claim_id}


# 1️⃣ Endpoint: Extract Aadhaar Number
@router.post("/extract-aadhaar")
async def extract_aadhaar(
    file: UploadFile = File(...),
    claim_id: Optional[str] = Query(None, description="Claim ID to update state")
):
    path = f"{UPLOAD_DIR}/{uuid.uuid4()}_{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())

    classifier = AadhaarClassifier()
    result = classifier.classify(path)
    
    # If claim_id provided, update the claim state
    if claim_id:
        state = claim_store.get_claim(claim_id)
        if not state:
            raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")
        
        # Update state with identity image path and run agent
        state["identity_image_path"] = path
        updated_state = identity_verification_agent(state)
        claim_store.update_claim(claim_id, updated_state)

    return {
        "aadhaar_numbers": result["aadhaar_numbers"],
        "verified": result["verified"],
        "aadhaar_name": result.get("aadhaar_name"),
        "aadhaar_age": result.get("aadhaar_age"),
        "claim_id": claim_id
    }
