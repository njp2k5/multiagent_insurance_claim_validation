from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import FAISS
from typing import List
import numpy as np

class SimpleEmbedding(Embeddings):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_query(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        # lightweight hash embedding (hackathon safe)
        np.random.seed(abs(hash(text)) % (2**32))
        return np.random.rand(384).tolist()

def build_vector_store(texts: List[str]) -> FAISS:
    docs = [Document(page_content=t) for t in texts]
    return FAISS.from_documents(docs, SimpleEmbedding())
