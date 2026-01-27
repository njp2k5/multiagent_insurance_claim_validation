from typing import List, TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from langchain_community.vectorstores import FAISS

# Lazy import for FAISS to avoid slow startup
_FAISS = None
_Document = None
_Embeddings = None


def _get_langchain_imports():
    """Lazy load langchain imports to speed up app startup."""
    global _FAISS, _Document, _Embeddings
    if _FAISS is None:
        from langchain_core.documents import Document
        from langchain_core.embeddings import Embeddings
        from langchain_community.vectorstores import FAISS
        _Document = Document
        _Embeddings = Embeddings
        _FAISS = FAISS
    return _Document, _Embeddings, _FAISS


class SimpleEmbedding:
    """Lightweight hash-based embedding for fast similarity search."""
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_query(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        # lightweight hash embedding (hackathon safe)
        np.random.seed(abs(hash(text)) % (2**32))
        return np.random.rand(384).tolist()


def build_vector_store(texts: List[str]) -> "FAISS":
    """Build FAISS vector store from texts. Imports are loaded lazily."""
    Document, Embeddings, FAISS = _get_langchain_imports()
    docs = [Document(page_content=t) for t in texts]
    return FAISS.from_documents(docs, SimpleEmbedding())
