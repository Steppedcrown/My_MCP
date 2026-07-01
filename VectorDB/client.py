from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

_STORE_PATH = Path(__file__).parent.parent / "vector_store.pkl"
_MODEL_NAME = "all-MiniLM-L6-v2"

_store: "VectorStore | None" = None


class VectorStore:
    """Lightweight numpy-backed vector store with a Chroma-compatible API."""

    def __init__(self):
        self._model = SentenceTransformer(_MODEL_NAME)
        self._ids: list[str] = []
        self._embeddings: np.ndarray | None = None
        self._documents: list[str] = []
        self._metadatas: list[dict] = []

    # ── Chroma-compatible interface ───────────────────────────────────────────

    def count(self) -> int:
        return len(self._ids)

    def upsert(
        self,
        ids: list[str],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        new_embs = self._model.encode(documents, normalize_embeddings=True)
        id_index = {doc_id: idx for idx, doc_id in enumerate(self._ids)}

        for i, doc_id in enumerate(ids):
            if doc_id in id_index:
                idx = id_index[doc_id]
                self._embeddings[idx] = new_embs[i]
                self._documents[idx] = documents[i]
                self._metadatas[idx] = metadatas[i]
            else:
                self._ids.append(doc_id)
                self._documents.append(documents[i])
                self._metadatas.append(metadatas[i])
                vec = new_embs[i : i + 1]
                self._embeddings = (
                    vec if self._embeddings is None
                    else np.vstack([self._embeddings, vec])
                )
                id_index[doc_id] = len(self._ids) - 1

    def query(
        self,
        query_texts: list[str],
        n_results: int = 5,
        where: dict | None = None,
        include: list[str] | None = None,
    ) -> dict:
        empty = {"documents": [[]], "metadatas": [[]], "distances": [[]]}
        if self._embeddings is None or not self._ids:
            return empty

        q_emb = self._model.encode(query_texts, normalize_embeddings=True)
        sims = np.dot(self._embeddings, q_emb.T).flatten().astype(float)

        if where:
            field, value = next(iter(where.items()))
            mask = np.array([m.get(field) == value for m in self._metadatas])
            sims = np.where(mask, sims, -np.inf)

        n = min(n_results, len(self._ids))
        order = np.argsort(sims)[::-1]
        top = [int(i) for i in order if sims[i] > -np.inf][:n]

        return {
            "documents": [[self._documents[i] for i in top]],
            "metadatas": [[self._metadatas[i] for i in top]],
            "distances": [[round(1.0 - float(sims[i]), 6) for i in top]],
        }

    # ── Persistence ───────────────────────────────────────────────────────────

    def save(self, path: Path = _STORE_PATH) -> None:
        with open(path, "wb") as f:
            pickle.dump(
                {
                    "ids": self._ids,
                    "embeddings": self._embeddings,
                    "documents": self._documents,
                    "metadatas": self._metadatas,
                },
                f,
            )

    @classmethod
    def load(cls, path: Path = _STORE_PATH) -> "VectorStore":
        store = cls.__new__(cls)
        store._model = SentenceTransformer(_MODEL_NAME)
        with open(path, "rb") as f:
            data = pickle.load(f)
        store._ids = data["ids"]
        store._embeddings = data["embeddings"]
        store._documents = data["documents"]
        store._metadatas = data["metadatas"]
        return store


def get_collection() -> VectorStore:
    global _store
    if _store is None:
        if _STORE_PATH.exists():
            _store = VectorStore.load(_STORE_PATH)
        else:
            _store = VectorStore()
    return _store
