from pathlib import Path
import re


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_KNOWLEDGE_BASE_CANDIDATES = (
    REPOSITORY_ROOT / "knowledge-base",
    REPOSITORY_ROOT / "knowlegde-base",
)
KNOWLEDGE_BASE_DIR = next(
    (path for path in _KNOWLEDGE_BASE_CANDIDATES if path.is_dir()),
    _KNOWLEDGE_BASE_CANDIDATES[0],
)

_TOPIC_KEYWORDS = {
    "anxiety.md": (
        "anxiety",
        "anxious",
        "worry",
        "worried",
        "panic",
        "panicking",
        "racing thoughts",
        "grounding",
        "breathing exercise",
        "nervous",
    ),
    "crisis_resources.md": (
        "crisis",
        "suicidal",
        "self-harm",
        "self harm",
        "can't stay safe",
        "cannot stay safe",
        "urgent help",
        "emergency help",
        "hotline",
    ),
    "healthy_relationships.md": (
        "relationship",
        "partner",
        "communication",
        "boundaries",
        "boundary",
        "conflict",
        "controlling",
        "manipulation",
    ),
    "sleep_wellness.md": (
        "sleep",
        "sleeping",
        "fall asleep",
        "can't fall asleep",
        "cannot fall asleep",
        "not able to fall asleep",
        "trouble sleeping",
        "difficulty sleeping",
        "insomnia",
        "waking up",
        "wake up",
        "restless",
        "bedtime",
        "sleep schedule",
        "tired",
        "fatigue",
        "exhausted",
    ),
    "stress_management.md": (
        "stress",
        "stressed",
        "stressful",
        "overwhelmed",
        "too much to do",
        "time management",
        "burned out",
        "burnt out",
        "tension",
        "pressure",
    ),
}


def get_relevant_knowledge(user_message: str) -> str:
    """Load the most relevant knowledge-base document(s) for a message."""
    normalized_message = " ".join(user_message.casefold().split())
    scores: dict[str, int] = {}

    for filename, keywords in _TOPIC_KEYWORDS.items():
        score = sum(
            1
            for keyword in keywords
            if re.search(
                rf"(?<!\w){re.escape(keyword)}(?!\w)",
                normalized_message,
            )
        )
        if score:
            scores[filename] = score

    if not scores:
        return ""

    highest_score = max(scores.values())
    selected_files = [
        filename for filename, score in scores.items()
        if score == highest_score
    ]

    sections = []
    for filename in selected_files:
        document_path = KNOWLEDGE_BASE_DIR / filename
        content = document_path.read_text(encoding="utf-8").strip()
        sections.append(f"### {filename}\n{content}")

    return "\n\n".join(sections)