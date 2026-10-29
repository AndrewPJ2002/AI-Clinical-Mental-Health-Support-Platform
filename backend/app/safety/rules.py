# red flag detection

from openai import OpenAI
from typing import Optional

from app.config import settings


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


def usr_message_check(
    message: str,
) -> Optional[str]:
    try:
        result = client.moderations.create(
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

    if (
        categories.self_harm
        or categories.self_harm_intent
        or categories.self_harm_instructions
    ):
        return "high"

    if (
        categories.violence
        or categories.illicit_violent
        or categories.harassment
    ):
        return "medium"

    return None


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