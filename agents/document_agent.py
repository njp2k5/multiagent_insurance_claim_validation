from state import ClaimState, AgentResult
from documents.ocr import extract_text_from_images_parallel, extract_patient_name_and_age
from documents.embeddings import build_vector_store
from documents.rag import summarize_documents

def document_validation_agent(state: ClaimState) -> ClaimState:
    image_paths = state.get("document_image_paths", [])

    # Use parallel OCR for faster processing
    texts = extract_text_from_images_parallel(image_paths)
    
    # Extract name and age from all documents
    extracted_name = None
    extracted_age = None
    for text in texts:
        name, age = extract_patient_name_and_age(text)
        if name and not extracted_name:
            extracted_name = name
        if age and not extracted_age:
            extracted_age = age
        if extracted_name and extracted_age:
            break

    # Handle empty texts case
    if not texts or all(not t.strip() for t in texts):
        summary = "No readable content found in the uploaded documents."
        context = ""
    else:
        vector_db = build_vector_store(texts)
        # Reduce k to 1 for faster retrieval with small doc sets
        k_value = max(1, min(len(texts), 2))
        retrieved = vector_db.similarity_search(
            "Summarize and validate insurance documents",
            k=k_value
        )

        context = "\n\n".join(d.page_content for d in retrieved)
        summary = summarize_documents(context) if context.strip() else "No content extracted from documents."

    status = "PASS" if summary else "INFO"
    
    # Store extracted name and age
    state["document_name"] = extracted_name
    state["document_age"] = extracted_age
    
    # Populate cross_agent_data for cross-validation
    cross_agent_data = state.get("cross_agent_data", {})
    cross_agent_data["document_name"] = extracted_name
    cross_agent_data["document_age"] = extracted_age
    state["cross_agent_data"] = cross_agent_data

    result: AgentResult = {
        "agent_name": "DocumentValidationAgent",
        "status": status,
        "confidence": 0.9 if status == "PASS" else 0.5,
        "message": (
            "Documents summarized successfully"
            if status == "PASS"
            else "Documents summarized"
        ),
        "metadata": {
            "summary": summary,
            "extracted_name": extracted_name,
            "extracted_age": extracted_age
        }
    }

    state["document_result"] = result
    state["document_summary"] = summary
    if "agent_results" not in state:
        state["agent_results"] = []
    state["agent_results"].append(result)

    return state

