# backend/tests/conftest.py
#
# Shared fixtures for the backend test suite.

import pytest
from fastapi.testclient import TestClient

import main
from cache import SimilarityCache


@pytest.fixture
def client() -> TestClient:
    return TestClient(main.app)


@pytest.fixture(autouse=True)
def reset_chat_cache():
    """Give every test a fresh SimilarityCache.

    WHY: main._chat_cache is a module-level singleton, so a cache hit
    recorded by one test would silently leak into the next test and make
    its assertions about cached/not-cached meaningless.
    """
    main._chat_cache = SimilarityCache()
    yield
