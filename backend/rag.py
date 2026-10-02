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

import hashlib
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

# WHY store a content hash in the collection's metadata: see
# _get_or_build_collection below. Counting rows can't detect that a skill's
# *text* changed, so we keep a fingerprint of the indexed content alongside it.
_FINGERPRINT_KEY = "content_fingerprint"

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

    WHY concatenate name + category + description + use_cases + job_relevance:
    a query like "what should I learn to get an ML job" matches job_relevance/
    use_cases text far better than it matches description alone. Embedding
    only description would miss those matches.

    WHY category is in here: it was originally omitted, and that was a real
    retrieval bug. Queries phrased by *job area* ("what should I learn for
    backend jobs?") had nothing to anchor to, because the literal word
    "Backend" only appeared in a skill's prose by luck. Measured before the
    fix: the top-4 for that query contained none of the 8 Backend-category
    skills, and FastAPI ranked #15 of 59. The category label is the single
    strongest signal for area-shaped queries, which are most of what a career
    advisor gets asked.

    WHY level is NOT in here: measured, and it's a genuine tradeoff rather
    than a win. Benchmarked over 6 area-shaped queries plus one level-shaped
    query ("what should a complete beginner learn first"):

        variant                 area queries   beginner-level in top-4
        baseline (no category)      5/6                 2/4
        + category                  6/6                 2/4
        + category + level          6/6                 4/4

    Adding level clearly helps level-shaped queries (2/4 -> 4/4), but it
    dilutes the category signal on the queries this app gets most: for "what
    should I learn for backend jobs?", +category puts 3 Backend skills in the
    top 4, while +category+level puts only 1 (best Backend rank slips #2 ->
    #3). Since +category alone regresses nothing versus baseline and level is
    a structured field the API already exposes for filtering, we take the
    no-regression option and leave level out of the embedding.
    ALTERNATIVE: embed each field as a separate Chroma document — more
    granular, but multiplies the collection size for no real precision gain
    at 59 rows, and complicates mapping results back to one Skill dict.
    """
    return (
        f"{skill['name']} ({skill['category']}). {skill['description']} "
        f"Use cases: {', '.join(skill['use_cases'])}. "
        f"{skill['job_relevance']}"
    )


def _fingerprint(documents: list[str]) -> str:
    """Short, stable hash of every document that will be indexed.

    WHY a NUL separator between documents: without it, ["ab", "c"] and
    ["a", "bc"] would hash identically. NUL can't appear in our source text,
    so it's an unambiguous boundary.
    WHY truncate to 16 hex chars: this only needs to detect accidental change,
    not resist an attacker. 64 bits is far more than enough, and it stays
    readable when inspecting the collection's metadata by hand.
    """
    digest = hashlib.sha256()
    for document in documents:
        digest.update(document.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()[:16]


def _get_or_build_collection() -> Collection:
    """Return the 'skills' collection, rebuilding it if it's absent or stale.

    WHY skip the rebuild when possible: on a warm restart with a persistent
    disk, the embeddings are already there — recomputing them would waste the
    ~1s (locally) it takes and, more importantly, waste the model-load time on
    constrained hosts. On Render's free tier the disk isn't persistent, so
    this rebuilds automatically on every boot anyway.

    WHY a fingerprint and not just count(): counting rows answers "how many
    skills are indexed?", never "is what's indexed still correct?". The
    original version returned early whenever count() == len(SKILLS), which
    meant any edit to a skill's text — or to _skill_to_text itself — was
    silently ignored on a machine with an existing chroma_data/ directory.
    The index would keep serving embeddings of text that no longer exists in
    the source. That failure was invisible on Render (ephemeral disk = cold
    rebuild every boot) and permanent locally, which is the worst possible
    split: it only breaks on the laptop you demo from.
    ALTERNATIVE 1: unconditionally delete-and-rebuild every startup — correct,
    but throws away the one real benefit of PersistentClient.
    ALTERNATIVE 2: bump a version suffix in _COLLECTION_NAME by hand on every
    KB edit — relies on remembering, and orphans old collections on disk.

    NOTE: get_or_create_collection() does NOT update the metadata of a
    collection that already exists (verified against chromadb 1.5.9) — it
    returns the stored metadata. That's exactly what we want: it lets us read
    the *old* fingerprint back to compare, and makes delete-then-recreate the
    only way the stored fingerprint changes.
    """
    documents = [_skill_to_text(skill) for skill in SKILLS]
    fingerprint = _fingerprint(documents)

    collection = _client.get_or_create_collection(
        name=_COLLECTION_NAME, metadata={_FINGERPRINT_KEY: fingerprint}
    )
    stored_fingerprint = (collection.metadata or {}).get(_FINGERPRINT_KEY)

    # Warm start: right number of rows AND the indexed text still matches.
    if collection.count() == len(SKILLS) and stored_fingerprint == fingerprint:
        return collection

    # Stale or partial. Drop it and rebuild so the stored fingerprint is
    # rewritten too. A collection we just created this call is already
    # correctly stamped and empty, so it needs no delete.
    if collection.count() > 0 or stored_fingerprint != fingerprint:
        _client.delete_collection(name=_COLLECTION_NAME)
        collection = _client.get_or_create_collection(
            name=_COLLECTION_NAME, metadata={_FINGERPRINT_KEY: fingerprint}
        )

    embeddings = _embedder.encode(documents).tolist()
    ids = [skill["id"] for skill in SKILLS]

    collection.add(ids=ids, embeddings=embeddings, documents=documents)
    return collection


_collection = _get_or_build_collection()

_SKILLS_BY_ID: dict[str, Skill] = {skill["id"]: skill for skill in SKILLS}


def embed(text: str) -> list[float]:
    """Embed a single string using the same model/instance the skill index uses.

    WHY expose this instead of having cache.py import the private _embedder
    directly: keeps rag.py's internal singleton private, and gives Step 4's
    cache the exact same embedding space search() uses, so a "similar query"
    means the same thing in both places.
    ALTERNATIVE: cache.py loads its own SentenceTransformer instance — wastes
    ~90MB of RAM loading the same model twice for no benefit.
    """
    return _embedder.encode([text])[0].tolist()


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
