from fastapi import APIRouter, UploadFile, File, HTTPException, Query
import os, uuid, shutil
from typing import Optional

from agents.document_agent import document_validation_agent
from documents.pdf_utils import pdf_to_images
from documents.ocr import extract_text_from_image, extract_patient_name_and_age
from state import ClaimState
from services.claim_store import claim_store

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = "uploads/documents"
IMAGE_DIR = f"{UPLOAD_DIR}/images"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

ALLOWED_TYPES = ["application/pdf", "image/png"]

@router.post("/upload-and-validate")
async def upload_and_validate(
    doc1: UploadFile = File(...),
    doc2: UploadFile = File(...),
    claim_id: Optional[str] = Query(None, description="Claim ID to update state")
):
    image_paths = []

    for doc in [doc1, doc2]:
        if doc.content_type not in ALLOWED_TYPES:
            raise HTTPException(400, "Only PDF or PNG files are allowed")

        temp_path = f"{UPLOAD_DIR}/{uuid.uuid4()}_{doc.filename}"
        with open(temp_path, "wb") as f:
            f.write(await doc.read())

        # PDF → images
        if doc.content_type == "application/pdf":
            image_paths.extend(pdf_to_images(temp_path, IMAGE_DIR))
        else:
            image_paths.append(temp_path)

    # Use existing claim state if claim_id provided, otherwise create new
    if claim_id:
        state = claim_store.get_claim(claim_id)
        if not state:
            raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")
        state["document_image_paths"] = image_paths
        if "agent_results" not in state:
            state["agent_results"] = []
    else:
        state: ClaimState = {
            "document_image_paths": image_paths,
            "agent_results": []
        }

    updated = document_validation_agent(state)
    result = updated.get("document_result")

    if not result:
        raise HTTPException(500, "Document validation failed")
    
    # Update claim store if claim_id was provided
    if claim_id:
        claim_store.update_claim(claim_id, updated)

    return {
        "summary": result["metadata"]["summary"],
        "agent_status": result["status"],
        "extracted_name": result["metadata"].get("extracted_name"),
        "extracted_age": result["metadata"].get("extracted_age"),
        "claim_id": claim_id
    }


@router.post("/extract-name-age")
async def extract_name_age(
    doc1: UploadFile = File(...),
    doc2: UploadFile = File(...)
):
    image_paths = []

    for doc in [doc1, doc2]:
        if doc.content_type not in ALLOWED_TYPES:
            raise HTTPException(400, "Only PDF or PNG files are allowed")

        temp_path = f"{UPLOAD_DIR}/{uuid.uuid4()}_{doc.filename}"
        with open(temp_path, "wb") as f:
            f.write(await doc.read())

        if doc.content_type == "application/pdf":
            image_paths.extend(pdf_to_images(temp_path, IMAGE_DIR))
        else:
            image_paths.append(temp_path)

    # Extract from first page/image only
    first_page_text = extract_text_from_image(image_paths[0]) if image_paths else ""
    doc_name, doc_age = extract_patient_name_and_age(first_page_text)

    return {
        "document_name": doc_name,
        "document_age": doc_age,
    }
