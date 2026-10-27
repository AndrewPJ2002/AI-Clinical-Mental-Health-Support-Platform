from app.knowledge_base import get_relevant_knowledge


def test_get_relevant_knowledge_selects_anxiety_document():
    knowledge = get_relevant_knowledge(
        "I've been feeling anxious and having racing thoughts."
    )

    assert "anxiety.md" in knowledge
    assert "Grounding techniques" in knowledge
    assert "Sleep & Wellness" not in knowledge


def test_get_relevant_knowledge_returns_empty_for_unmatched_message():
    assert get_relevant_knowledge("What is your favorite color?") == ""
