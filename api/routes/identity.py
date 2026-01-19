from fastapi import APIRouter, UploadFile, File
import uuid, os

from identity.classifier import AadhaarClassifier
from agents.identity_agent import identity_verification_agent
from state import ClaimState

router = APIRouter(prefix="/identity", tags=["Identity"])

UPLOAD_DIR = "uploads/identity"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 1️⃣ Endpoint: Extract Aadhaar Number
@router.post("/extract-aadhaar")
async def extract_aadhaar(file: UploadFile = File(...)):
    path = f"{UPLOAD_DIR}/{uuid.uuid4()}_{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())

    classifier = AadhaarClassifier()
    result = classifier.classify(path)

    return {
        "aadhaar_numbers": result["aadhaar_numbers"],
        "verified": result["verified"],
        "aadhaar_name": result.get("aadhaar_name"),
        "aadhaar_age": result.get("aadhaar_age")
    }
