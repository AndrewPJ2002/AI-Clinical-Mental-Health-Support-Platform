# red flag detection

from openai import OpenAI
from typing import Optional

from app.config import settings
from app.db_tables import ModerationCategorySetting
from sqlalchemy.orm import Session
from app.ai_settings import get_ai_runtime_settings


# rule-based approach / binary
CRISIS_DICT = [

    # direct suicide references
    "kill myself", "killing myself", "end my life", "take my own life",
    "take my life", "commit suicide", "suicidal", "suicide",
    "want to die", "wanna die", "wish i was dead", "wish i were dead",
    "better off dead", "better off without me", "don't want to be alive",
    "do not want to be alive", "don't want to live", "no reason to live",
    "not worth living", "life isn't worth living", "end it all",
    "ending it all", "going to end it", "make it stop for good",

    # self harm
    "hurt myself", "hurting myself", "harm myself", "harming myself",
    "self harm", "self-harm", "selfharm", "cut myself", "cutting myself",
    "self-injury", "self injury", "self-injure", "self injure",

    # referencing plans
    "suicide plan", "suicide note", "goodbye note", "final goodbye",
    "saying goodbye to everyone", "giving away my things",
    "won't be around much longer", "this is my last day",
    "i want to disappear forever",

    # slang, informal expressions
    "unalive", "unalive myself", "kms", "kys", "k1ll",
    "sewerslide", "sui", "s*icide", "su1cide",
]


def contains_crisis(text: str) -> bool:
    lowered_text = text.lower()

    return any(
        word in lowered_text
        for word in CRISIS_DICT
    )


# Moderation API OpenAI
client = OpenAI(
    api_key=settings.open_api_key,
)

MODERATION_CATEGORIES = {
    "harassment": ("Harassment", "medium"),
    "harassment_threatening": ("Threatening harassment", "high"),
    "hate": ("Hate", "medium"),
    "hate_threatening": ("Threatening hate", "high"),
    "illicit": ("Illicit content", "medium"),
    "illicit_violent": ("Violent illicit content", "medium"),
    "self_harm": ("Self-harm", "high"),
    "self_harm_intent": ("Self-harm intent", "high"),
    "self_harm_instructions": ("Self-harm instructions", "high"),
    "sexual": ("Sexual content", "medium"),
    "sexual_minors": ("Sexual content involving minors", "high"),
    "violence": ("Violence", "medium"),
    "violence_graphic": ("Graphic violence", "high"),
}
DEFAULT_ENABLED_CATEGORIES = {
    "harassment", "illicit_violent", "self_harm", "self_harm_intent",
    "self_harm_instructions", "violence",
}

SEVERITY_ORDER = {"low": 1, "medium": 2, "high": 3}


def get_moderation_category_settings(db: Session | None = None) -> list[dict]:
    stored = {}
    if db is not None:
        stored = {
            row.category: row
            for row in db.query(ModerationCategorySetting).all()
        }
    return [
        {
            "category": category,
            "label": label,
            "severity": stored[category].severity if category in stored else default_severity,
            "is_enabled": (
                stored[category].is_enabled
                if category in stored
                else category in DEFAULT_ENABLED_CATEGORIES
            ),
        }
        for category, (label, default_severity) in MODERATION_CATEGORIES.items()
    ]


def moderation_check(message: str, db: Session | None = None) -> dict:
    try:
        moderation_client = client
        if db is not None:
            ai_settings = get_ai_runtime_settings(db)
            if not ai_settings["api_key"]:
                raise RuntimeError("The AI API key is not configured.")
            moderation_client = OpenAI(api_key=ai_settings["api_key"])
        result = moderation_client.moderations.create(
            model="omni-moderation-latest",
            input=message,
        )

    except Exception as exc:
        raise RuntimeError(
            "The moderation service is unavailable."
        ) from exc

    if not result.results:
        raise RuntimeError(
            "The moderation service returned no results."
        )

    moderation = result.results[0]
    categories = moderation.categories

    matches = [
        setting
        for setting in get_moderation_category_settings(db)
        if setting["is_enabled"]
        and bool(getattr(categories, setting["category"], False))
    ]
    severity = max(
        (setting["severity"] for setting in matches),
        key=lambda value: SEVERITY_ORDER[value],
        default=None,
    )
    return {
        "severity": severity,
        "categories": [setting["category"] for setting in matches],
    }


def usr_message_check(message: str, db: Session | None = None) -> Optional[str]:
    """Compatibility helper returning only the highest matched severity."""
    return moderation_check(message, db)["severity"]


# ___Hardcoded test cases___
'''
message = "I want to kill myself"
red_flag = usr_message_check(message)
print(f"Message 1: {message}\\nRed Flag Level: {red_flag}")

message1 = "I want to shoot this person"
red_flag1 = usr_message_check(message1)
print(f"Message 2: {message1}\\nRed Flag Level: {red_flag1}")

message2 = "I have been so depresed lately"
red_flag2 = usr_message_check(message2)
print(f"Message 3: {message2}\\nRed Flag Level: {red_flag2}")
'''
