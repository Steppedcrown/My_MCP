from __future__ import annotations
from pathlib import Path

try:
    import chromadb
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    _CHROMADB_AVAILABLE = True
except ImportError:
    _CHROMADB_AVAILABLE = False

_CHROMA_PATH = str(Path(__file__).parent.parent / "chroma_data")

_client = None
_collection = None


def get_collection():
    if not _CHROMADB_AVAILABLE:
        raise RuntimeError(
            "chromadb is not installed. Install it and set VECTORDB_ENABLED=1 "
            "to enable vector search."
        )
    global _client, _collection
    if _collection is None:
        _EF = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        _client = chromadb.PersistentClient(path=_CHROMA_PATH)
        _collection = _client.get_or_create_collection(
            name="elden_ring",
            embedding_function=_EF,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection
