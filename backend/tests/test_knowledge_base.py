# backend/tests/test_knowledge_base.py
#
# Pins the schema invariants that validate_skills() already enforces at
# import time, plus a few structural checks on the dataset itself.

from knowledge_base import SKILLS

_ALLOWED_CATEGORIES = {
    "Programming Language",
    "Backend",
    "Frontend Framework",
    "Full-Stack Framework",
    "Database",
    "AI/ML",
    "AI/ML Infrastructure",
    "DevOps",
    "Cloud",
    "Developer Tool",
    "Software Engineering",
    "Computer Science",
}
_ALLOWED_LEVELS = {"beginner", "intermediate", "advanced"}


def test_has_at_least_fifty_skills():
    assert len(SKILLS) >= 50


def test_ids_are_unique():
    ids = [skill["id"] for skill in SKILLS]
    assert len(ids) == len(set(ids))


def test_every_skill_has_required_fields():
    required_fields = {
        "id", "name", "category", "description", "level", "estimated_weeks",
        "prerequisites", "leads_to", "use_cases", "resources", "job_relevance",
    }
    for skill in SKILLS:
        missing = required_fields - skill.keys()
        assert not missing, f"{skill['id']} is missing fields: {missing}"


def test_categories_and_levels_are_valid():
    for skill in SKILLS:
        assert skill["category"] in _ALLOWED_CATEGORIES, skill["id"]
        assert skill["level"] in _ALLOWED_LEVELS, skill["id"]


def test_prerequisites_and_leads_to_reference_real_ids():
    ids = {skill["id"] for skill in SKILLS}
    for skill in SKILLS:
        for ref_id in skill["prerequisites"] + skill["leads_to"]:
            assert ref_id in ids, f"{skill['id']} references unknown id '{ref_id}'"


def test_all_twelve_categories_are_represented():
    represented = {skill["category"] for skill in SKILLS}
    assert represented == _ALLOWED_CATEGORIES
