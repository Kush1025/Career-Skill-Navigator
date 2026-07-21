# backend/cache.py
#
# A semantic cache that sits in front of the Claude API call in Step 5's
# /chat endpoint. Exact-string caching would miss most real hits, since users
# rarely phrase the same intent identically — this compares queries by
# embedding similarity instead.
#
# WHY a class with get()/set() instead of two free functions: the cache needs
# to hold mutable state (the list of cached entries) between calls, and a
# class makes that ownership explicit. It also gives us one clear seam to
# swap in a Redis-backed implementation later without touching call sites.
# ALTERNATIVE: a module-level list + two functions closing over it — works,
# but hides the "this is stateful" fact and makes testing with a fresh cache
# per-test more awkward (would need a reset() function instead of just
# instantiating a new object).

from dataclasses import dataclass

from rag import embed

# WHY 0.92: matches the threshold documented in CLAUDE.md's architecture
# diagram. High enough that two different questions ("learn React" vs "learn
# Vue") don't collide, but forgiving enough that paraphrases of the same
# question ("skills for backend jobs" vs "what backend skills should I learn")
# do hit.
DEFAULT_SIMILARITY_THRESHOLD = 0.92


@dataclass
class _CacheEntry:
    query_embedding: list[float]
    response: str


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two equal-length vectors, in [-1, 1].

    WHY hand-rolled instead of numpy/scipy: avoids adding a numpy dependency
    to this module for three lines of arithmetic on ~384-dim vectors — plain
    Python floats are plenty fast at this scale (cache sizes in the dozens).
    ALTERNATIVE: numpy.dot / norm — faster at large scale, but numpy is
    already a transitive dependency via sentence-transformers/torch, so this
    is a style choice, not a real cost tradeoff.
    """
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    return dot / (norm_a * norm_b)


class SimilarityCache:
    """In-memory cache of (query embedding -> response) pairs.

    WHY linear scan over all entries on every get(): simple, no extra index
    structure to maintain, and completely fine at the scale this demo will
    ever see (a single server's worth of chat queries, not millions).
    ALTERNATIVE: a real vector index (e.g. reuse ChromaDB for the cache too)
    — would matter at thousands of cached entries, but is unneeded complexity
    here and would tie the cache's lifetime to disk instead of the process.
    """

    def __init__(self, threshold: float = DEFAULT_SIMILARITY_THRESHOLD) -> None:
        self._threshold = threshold
        self._entries: list[_CacheEntry] = []

    def get(self, query: str) -> str | None:
        """Return a cached response if a similar-enough query was seen before,
        else None.
        """
        if not self._entries:
            return None

        query_embedding = embed(query)
        best_entry = max(
            self._entries,
            key=lambda entry: _cosine_similarity(query_embedding, entry.query_embedding),
        )
        best_similarity = _cosine_similarity(query_embedding, best_entry.query_embedding)

        if best_similarity >= self._threshold:
            return best_entry.response
        return None

    def set(self, query: str, response: str) -> None:
        """Cache a response against the embedding of its query."""
        self._entries.append(_CacheEntry(query_embedding=embed(query), response=response))
