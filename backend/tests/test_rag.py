# backend/tests/test_rag.py
#
# Uses the real sentence-transformers model and ChromaDB index — both run
# locally at zero cost, so there's no reason to mock them. Mocking would
# hide actual retrieval regressions.

from rag import search


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
