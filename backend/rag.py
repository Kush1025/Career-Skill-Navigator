# backend/rag.py
#
# The retrieval half of RAG. Turns the static SKILLS list from Step 2 into a
# semantically searchable index, and exposes search() so Step 5's /chat and
# /search endpoints can pull the top-matching skills for a user's query.
#
# WHY a persistent ChromaDB collection instead of re-embedding on every query:
# embedding is the expensive part (loading + running the model), so we do it
# once at startup and let Chroma do fast vector lookups after that.
# ALTERNATIVE: embed the query and every skill on every request — simple, but
# wastes CPU recomputing the same 59 skill embeddings on every single call.

from pathlib import Path

import chromadb
from chromadb.api.models.Collection import Collection
from sentence_transformers import SentenceTransformer

from knowledge_base import SKILLS, Skill

# WHY a path relative to this file (not the CWD): uvicorn/pytest may be
# launched from different working directories, and a CWD-relative path would
# silently create a second, empty database instead of finding the real one.
# ALTERNATIVE: a bare relative path like "chroma_data" — fragile, breaks the
# moment this module is imported from anywhere other than backend/.
_CHROMA_DIR = Path(__file__).parent / "chroma_data"
_COLLECTION_NAME = "skills"

# WHY module-level singletons instead of re-creating per call: loading the
# embedding model (~90MB) and opening the Chroma client are both slow-ish
# one-time costs. Every function below reuses these instead of re-paying it.
# ALTERNATIVE: wrap these in a class instantiated once in main.py — more
# "proper" OOP, but for a single-process script this is the same effect with
# less ceremony.
_embedder = SentenceTransformer("all-MiniLM-L6-v2")
_client = chromadb.PersistentClient(path=str(_CHROMA_DIR))


def _skill_to_text(skill: Skill) -> str:
    """Flatten one skill dict into a single text blob for embedding.

    WHY concatenate name + description + use_cases + job_relevance: a query
    like "what should I learn to get an ML job" matches job_relevance/
    use_cases text far better than it matches description alone. Embedding
    only description would miss those matches.
    ALTERNATIVE: embed each field as a separate Chroma document — more
    granular, but multiplies the collection size for no real precision gain
    at 59 rows, and complicates mapping results back to one Skill dict.
    """
    return (
        f"{skill['name']}. {skill['description']} "
        f"Use cases: {', '.join(skill['use_cases'])}. "
        f"{skill['job_relevance']}"
    )


def _get_or_build_collection() -> Collection:
    """Return the 'skills' collection, building it from SKILLS if empty.

    WHY check count() instead of always re-embedding: on a warm restart with
    a persistent disk, the embeddings are already on disk — recomputing them
    would waste the ~1s (locally) it takes and, more importantly, waste the
    model-load time on constrained hosts. On Render's free tier the disk
    isn't persistent, so this rebuilds automatically on every boot anyway.
    ALTERNATIVE: unconditionally delete-and-rebuild on every startup — simpler
    but throws away the one real benefit of PersistentClient.
    """
    collection = _client.get_or_create_collection(name=_COLLECTION_NAME)

    if collection.count() == len(SKILLS):
        return collection

    # Rebuild from scratch: fine at 59 rows, and guards against a stale
    # index left over from a previous, different version of knowledge_base.py.
    if collection.count() > 0:
        _client.delete_collection(name=_COLLECTION_NAME)
        collection = _client.get_or_create_collection(name=_COLLECTION_NAME)

    documents = [_skill_to_text(skill) for skill in SKILLS]
    embeddings = _embedder.encode(documents).tolist()
    ids = [skill["id"] for skill in SKILLS]

    collection.add(ids=ids, embeddings=embeddings, documents=documents)
    return collection


_collection = _get_or_build_collection()

_SKILLS_BY_ID: dict[str, Skill] = {skill["id"]: skill for skill in SKILLS}


def search(query: str, top_k: int = 4) -> list[Skill]:
    """Return the top_k skills whose embedding is closest to the query.

    WHY return full Skill dicts instead of raw Chroma results: callers (the
    /chat prompt builder, the /search endpoint) want the same shape as
    everything else in the app, not Chroma's internal result format.
    ALTERNATIVE: return Chroma's raw QueryResult — leaks a third-party
    library's data shape into the rest of the app for no benefit.
    """
    query_embedding = _embedder.encode([query]).tolist()
    results = _collection.query(query_embeddings=query_embedding, n_results=top_k)
    matched_ids = results["ids"][0]
    return [_SKILLS_BY_ID[skill_id] for skill_id in matched_ids]
