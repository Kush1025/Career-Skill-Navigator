# backend/tests/test_rag.py
#
# Uses the real sentence-transformers model and ChromaDB index — both run
# locally at zero cost, so there's no reason to mock them. Mocking would
# hide actual retrieval regressions.

import pytest

from rag import _fingerprint, _skill_to_text, search


def test_search_returns_requested_count():
    results = search("learn to build a web backend", top_k=3)
    assert len(results) == 3


def test_search_returns_known_skill_ids():
    from knowledge_base import SKILLS

    known_ids = {skill["id"] for skill in SKILLS}
    results = search("how do I get started with machine learning", top_k=4)
    assert all(skill["id"] in known_ids for skill in results)


def test_search_finds_topically_relevant_skill():
    results = search("I want to learn about neural networks and deep learning", top_k=5)
    categories = {skill["category"] for skill in results}
    assert "AI/ML" in categories


# WHY parametrize over several job areas instead of testing one: this is the
# regression guard for the category-embedding fix. Before category was part of
# the embedded text, "what should I learn for backend jobs?" returned zero
# Backend-category skills in its top 4 (best Backend skill ranked #6 of 59,
# FastAPI #15). One query passing could be luck; six holding is the property
# we actually care about — area-shaped queries retrieve that area's skills.
@pytest.mark.parametrize(
    "query,expected_category",
    [
        ("what should I learn for backend jobs?", "Backend"),
        ("how do I get into frontend development", "Frontend Framework"),
        ("I want a job in machine learning", "AI/ML"),
        ("what databases should I learn", "Database"),
        ("how do I learn devops and deployment", "DevOps"),
        ("which cloud skills matter for jobs", "Cloud"),
    ],
)
def test_area_query_retrieves_that_area(query: str, expected_category: str):
    results = search(query, top_k=4)
    categories = [skill["category"] for skill in results]
    assert expected_category in categories, (
        f"'{query}' returned {categories}, expected a {expected_category} skill"
    )


def test_skill_text_includes_category():
    """Pins the specific field whose absence caused the retrieval bug.

    WHY assert on the text and not only on search results: if someone drops
    category from _skill_to_text, the parametrized test above tells you
    retrieval broke but not why. This one names the cause directly.
    """
    skill = {
        "name": "FastAPI",
        "category": "Backend",
        "description": "A Python web framework.",
        "use_cases": ["APIs"],
        "job_relevance": "In demand.",
    }
    assert "Backend" in _skill_to_text(skill)


def test_fingerprint_changes_when_content_changes():
    """The staleness check is only as good as this hash.

    WHY the third case: without a separator between documents, ["ab", "c"]
    and ["a", "bc"] concatenate to the same bytes and would collide, letting
    a real content change slip past as a warm start.
    """
    assert _fingerprint(["a", "b"]) == _fingerprint(["a", "b"])
    assert _fingerprint(["a", "b"]) != _fingerprint(["a", "B"])
    assert _fingerprint(["ab", "c"]) != _fingerprint(["a", "bc"])
    assert _fingerprint(["a", "b"]) != _fingerprint(["b", "a"])


def test_index_is_not_stale():
    """The live collection's fingerprint must match the current source text.

    WHY this test exists: it is the one that would have caught the original
    bug. count() == len(SKILLS) was treated as "index is fine", so edits to
    knowledge_base.py or _skill_to_text were ignored on any machine with an
    existing chroma_data/ directory.
    """
    from knowledge_base import SKILLS
    from rag import _FINGERPRINT_KEY, _collection

    expected = _fingerprint([_skill_to_text(skill) for skill in SKILLS])
    assert (_collection.metadata or {}).get(_FINGERPRINT_KEY) == expected
    assert _collection.count() == len(SKILLS)
