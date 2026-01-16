from fastapi import APIRouter, UploadFile, File, HTTPException
import os, uuid, shutil

from agents.document_agent import document_validation_agent
from documents.pdf_utils import pdf_to_images
from state import ClaimState

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = "uploads/documents"
IMAGE_DIR = f"{UPLOAD_DIR}/images"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

ALLOWED_TYPES = ["application/pdf", "image/png"]

@router.post("/upload-and-validate")
async def upload_and_validate(
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

        # PDF → images
        if doc.content_type == "application/pdf":
            image_paths.extend(pdf_to_images(temp_path, IMAGE_DIR))
        else:
            image_paths.append(temp_path)

    state: ClaimState = {
        "document_image_paths": image_paths,
        "agent_results": []
    }

    updated = document_validation_agent(state)
    result = updated.get("document_result")

    if not result:
        raise HTTPException(500, "Document validation failed")

    return {
        "summary": result["metadata"]["summary"],
        "validation_score": result["metadata"]["validation_score"],
        "agent_status": result["status"]
    }
