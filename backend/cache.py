# backend/cache.py
#
# A semantic cache that sits in front of the Groq API call in Step 5's /chat
# endpoint. Exact-string caching would miss most real hits, since users
# rarely phrase the same intent identically — this compares queries by
# embedding similarity instead. See DEFAULT_SIMILARITY_THRESHOLD below for
# measured numbers on how well that actually works in practice.
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
# diagram. Measured behaviour against a cached "what should I learn for
# backend jobs?" (all-MiniLM-L6-v2, cosine):
#
#     1.0000  HIT   what should I learn for backend jobs?   (exact)
#     0.9935  HIT   What should I learn for backend jobs    (case/punct only)
#     0.8765  miss  what should I learn for FRONTEND jobs?
#     0.8735  miss  which backend skills should I learn
#     0.8446  miss  skills for backend jobs
#     0.6596  miss  how do I become a backend engineer
#    -0.0274  miss  best pizza in Chicago
#
# So be honest about what this is: at 0.92 it catches casing and punctuation
# variants, not true paraphrases. An earlier version of this comment claimed
# paraphrases like "skills for backend jobs" do hit — they do not.
#
# WHY NOT just lower the threshold: look at rows 3 and 4. The *frontend*
# question (0.8765) scores HIGHER than a legitimate backend paraphrase
# (0.8735). There is no threshold that admits the paraphrase while rejecting
# the wrong-domain query — the distributions overlap, so loosening this trades
# a cheap miss for a confidently wrong answer. A miss costs one Groq call; a
# false hit serves backend advice to someone asking about frontend.
#
# The real fix would be to cache on the retrieved skill IDs rather than on the
# raw query (two questions retrieving the same 4 skills are genuinely
# interchangeable), which sidesteps the overlap entirely. Left as a documented
# improvement rather than silently tuning a number that cannot work.
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
