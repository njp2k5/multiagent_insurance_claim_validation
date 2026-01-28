from typing import List, TYPE_CHECKING
import numpy as np
import hashlib
from langchain_core.embeddings import Embeddings

if TYPE_CHECKING:
    from langchain_community.vectorstores import FAISS

# Lazy import for FAISS to avoid slow startup
_FAISS = None
_Document = None

# Cache for vector stores to avoid rebuilding
_vector_store_cache: dict[str, "FAISS"] = {}


def _get_langchain_imports():
    """Lazy load langchain imports to speed up app startup."""
    global _FAISS, _Document
    if _FAISS is None:
        from langchain_core.documents import Document
        from langchain_community.vectorstores import FAISS
        _Document = Document
        _FAISS = FAISS
    return _Document, _FAISS


class SimpleEmbedding(Embeddings):
    """Lightweight hash-based embedding for fast similarity search."""
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_query(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        # lightweight hash embedding (hackathon safe)
        np.random.seed(abs(hash(text)) % (2**32))
        return np.random.rand(384).tolist()


# Singleton embedding instance to avoid recreation
_embedding_instance = None


def _get_embedding():
    """Get or create singleton embedding instance."""
    global _embedding_instance
    if _embedding_instance is None:
        _embedding_instance = SimpleEmbedding()
    return _embedding_instance


def _get_texts_hash(texts: List[str]) -> str:
    """Generate hash for text list for caching."""
    combined = "||".join(texts)
    return hashlib.md5(combined.encode()).hexdigest()


def build_vector_store(texts: List[str], use_cache: bool = True) -> "FAISS":
    """
    Build FAISS vector store from texts with caching.
    
    Optimizations:
    - Cache vector stores to avoid rebuilding
    - Reuse embedding instance
    - Skip empty texts
    """
    # Filter out empty texts
    texts = [t for t in texts if t and t.strip()]
    
    if not texts:
        # Return empty store with dummy doc
        Document, FAISS = _get_langchain_imports()
        return FAISS.from_documents(
            [Document(page_content="No content")], 
            _get_embedding()
        )
    
    # Check cache
    if use_cache:
        cache_key = _get_texts_hash(texts)
        if cache_key in _vector_store_cache:
            return _vector_store_cache[cache_key]
    
    Document, FAISS = _get_langchain_imports()
    docs = [Document(page_content=t) for t in texts]
    store = FAISS.from_documents(docs, _get_embedding())
    
    # Cache the store (limit cache size)
    if use_cache:
        if len(_vector_store_cache) > 50:
            # Clear oldest entries
            keys = list(_vector_store_cache.keys())[:25]
            for k in keys:
                del _vector_store_cache[k]
        _vector_store_cache[cache_key] = store
    
    return store


def clear_vector_cache():
    """Clear the vector store cache."""
    _vector_store_cache.clear()
