# backend/tests/test_cache.py
#
# Uses the real embedder (free, local) so the threshold behavior tested here
# reflects what actually happens in production, not a mocked approximation.

from cache import SimilarityCache


def test_miss_on_empty_cache():
    cache = SimilarityCache()
    assert cache.get("what should I learn for backend jobs") is None


def test_exact_repeat_hits():
    cache = SimilarityCache()
    cache.set("what should I learn for backend jobs", "Learn Python and FastAPI.")
    assert cache.get("what should I learn for backend jobs") == "Learn Python and FastAPI."


def test_unrelated_query_misses():
    cache = SimilarityCache()
    cache.set("what should I learn for backend jobs", "Learn Python and FastAPI.")
    assert cache.get("how do I learn to play guitar") is None


def test_paraphrase_respects_configured_threshold():
    """A near-paraphrase (~0.89 cosine similarity, verified manually in Step
    4) sits below the default 0.92 threshold but above a looser one — this
    pins that the threshold is actually load-bearing, not decorative.
    """
    strict_cache = SimilarityCache(threshold=0.92)
    loose_cache = SimilarityCache(threshold=0.85)

    for cache in (strict_cache, loose_cache):
        cache.set("what should I learn for backend jobs", "Learn Python and FastAPI.")

    paraphrase = "what backend skills should I learn"
    assert strict_cache.get(paraphrase) is None
    assert loose_cache.get(paraphrase) == "Learn Python and FastAPI."
