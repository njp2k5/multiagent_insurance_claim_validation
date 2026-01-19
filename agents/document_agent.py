from state import ClaimState, AgentResult
from documents.ocr import extract_text_from_image
from documents.embeddings import build_vector_store
from documents.rag import summarize_documents

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

    status = "PASS" if summary else "INFO"

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
        }
    }

    state["document_result"] = result
    state["document_summary"] = summary
    if "agent_results" not in state:
        state["agent_results"] = []
    state["agent_results"].append(result)

    return state

