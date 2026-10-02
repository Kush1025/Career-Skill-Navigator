# backend/tests/test_cache.py
#
# Uses the real embedder (free, local) so the threshold behavior tested here
# reflects what actually happens in production, not a mocked approximation.

from cache import DEFAULT_SIMILARITY_THRESHOLD, SimilarityCache, _cosine_similarity
from rag import embed


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
    """A near-paraphrase (0.8735 cosine, re-measured — an earlier version of
    this docstring said ~0.89) sits below the default 0.92 threshold but above
    a looser one — this pins that the threshold is load-bearing, not
    decorative.
    """
    strict_cache = SimilarityCache(threshold=0.92)
    loose_cache = SimilarityCache(threshold=0.85)

    for cache in (strict_cache, loose_cache):
        cache.set("what should I learn for backend jobs", "Learn Python and FastAPI.")

    paraphrase = "what backend skills should I learn"
    assert strict_cache.get(paraphrase) is None
    assert loose_cache.get(paraphrase) == "Learn Python and FastAPI."


def test_casing_and_punctuation_variants_hit():
    """What the 0.92 threshold actually buys us, stated as a test.

    WHY pin this: it's the honest scope of the cache. Users retyping a
    question with different capitalisation get a free hit; genuine
    rephrasings do not.
    """
    cache = SimilarityCache()
    cache.set("what should I learn for backend jobs?", "Learn Python and FastAPI.")
    assert cache.get("What should I learn for backend jobs") == "Learn Python and FastAPI."


def test_wrong_domain_outscores_valid_paraphrase():
    """Documents why lowering the threshold is NOT the fix for cache misses.

    A frontend question scores HIGHER against a cached backend question
    (0.8765) than a legitimate backend paraphrase does (0.8735). The
    distributions overlap, so no threshold admits the paraphrase while
    rejecting the wrong-domain query. If this assertion ever flips, the
    reasoning in cache.py's threshold comment needs revisiting.
    """
    cached_query = "what should I learn for backend jobs?"
    cached_embedding = embed(cached_query)

    valid_paraphrase = _cosine_similarity(
        embed("which backend skills should I learn"), cached_embedding
    )
    wrong_domain = _cosine_similarity(
        embed("what should I learn for frontend jobs?"), cached_embedding
    )

    assert wrong_domain > valid_paraphrase
    # ...and both land below the configured threshold, so today's behaviour
    # is "miss both", which is the safe side of the tradeoff.
    assert max(wrong_domain, valid_paraphrase) < DEFAULT_SIMILARITY_THRESHOLD


def test_threshold_rejects_unrelated_topic_decisively():
    """Sanity floor: an off-domain query should not be anywhere near the line.

    WHY: if an unrelated query ever scored close to the threshold, that would
    mean the embedding space had collapsed and the cache was unsafe at any
    setting.
    """
    cached_embedding = embed("what should I learn for backend jobs?")
    similarity = _cosine_similarity(embed("best pizza in Chicago"), cached_embedding)
    assert similarity < 0.3
