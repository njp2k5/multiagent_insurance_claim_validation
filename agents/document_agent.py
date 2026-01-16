from state import ClaimState, AgentResult
from documents.ocr import extract_text_from_image
from documents.embeddings import build_vector_store
from documents.rag import summarize_documents
from documents.validation import calculate_validation_score

def document_validation_agent(state: ClaimState) -> ClaimState:
    image_paths = state.get("document_image_paths", [])

    texts = [extract_text_from_image(p) for p in image_paths]

    vector_db = build_vector_store(texts)
    retrieved = vector_db.similarity_search(
        "Summarize and validate insurance documents",
        k=2
    )

    context = "\n\n".join(d.page_content for d in retrieved)
    summary = summarize_documents(context)

    validation_score = calculate_validation_score(texts)
    status = "PASS" if validation_score >= 0.6 else "FAIL"

    result: AgentResult = {
        "agent_name": "DocumentValidationAgent",
        "status": status,
        "confidence": round(validation_score, 2),
        "message": (
            "Documents appear legitimate"
            if status == "PASS"
            else "Documents require manual review"
        ),
        "metadata": {
            "summary": summary,
            "validation_score": round(validation_score, 2)
        }
    }

    state["document_result"] = result
    state["document_summary"] = summary
    state["document_validation_score"] = round(validation_score, 2)
    if "agent_results" not in state:
        state["agent_results"] = []
    state["agent_results"].append(result)

    return state

