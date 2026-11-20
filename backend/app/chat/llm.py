from typing import Mapping, Sequence

from openai import OpenAI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import engine
from app.db_tables import AIModelUsage
from app.ai_settings import get_ai_runtime_settings


# OpenAI standard text-token rates per million tokens. Keep unknown models
# unpriced instead of displaying an invented cost.
MODEL_RATES_USD_PER_MILLION = {
    "gpt-6-luna": {"input": 0.10, "cached_input": 0.01, "output": 0.50},
}
FALLBACK_MODEL = "gpt-6-luna"


def ensure_usage_table() -> None:
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS ai_model_usage (
                id BIGSERIAL PRIMARY KEY,
                model VARCHAR NOT NULL,
                input_tokens BIGINT NOT NULL,
                output_tokens BIGINT NOT NULL,
                cached_input_tokens BIGINT NOT NULL DEFAULT 0,
                cost_usd DOUBLE PRECISION,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """))


def _record_usage(db: Session, response, model: str) -> None:
    usage = response.usage
    if usage is None:
        return

    input_tokens = int(usage.prompt_tokens or 0)
    output_tokens = int(usage.completion_tokens or 0)
    details = usage.prompt_tokens_details
    cached_tokens = min(
        input_tokens,
        int(getattr(details, "cached_tokens", 0) or 0),
    )
    rates = MODEL_RATES_USD_PER_MILLION.get(
        model,
        MODEL_RATES_USD_PER_MILLION[FALLBACK_MODEL],
    )
    cost = (
        (input_tokens - cached_tokens) * rates["input"]
        + cached_tokens * rates["cached_input"]
        + output_tokens * rates["output"]
    ) / 1_000_000

    ensure_usage_table()
    db.add(AIModelUsage(
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cached_input_tokens=cached_tokens,
        cost_usd=cost,
    ))


SYSTEM_PROMPT = """
You are a supportive mental health companion.

Be empathetic, respectful, and nonjudgmental. Listen carefully and
respond in a calm, supportive manner.

You are not a therapist, doctor, or emergency service. Do not diagnose
conditions or claim to provide professional treatment.

If the user appears to be in immediate danger, encourage them to contact
local emergency services or a trusted person who can help.
"""


def build_prompt(
    conversation_history: Sequence[Mapping[str, str]],
    user_message: str,
    knowledge_context: str = "",
) -> list[dict[str, str]]:
    """Build the OpenAI chat messages from prior turns and the current message."""

    system_content = SYSTEM_PROMPT

    if knowledge_context.strip():
        system_content += (
            "\n\nRETRIEVED KNOWLEDGE-BASE CONTENT\n"
            "--------------------------------\n"
            f"{knowledge_context}\n\n"
            "Use the retrieved content when it is relevant to the user's "
            "question. Do not invent facts, citations, or resources, and "
            "do not claim that information comes from the knowledge base "
            "unless it appears in the retrieved content. If the retrieved "
            "content does not answer the question, be transparent about "
            "that limitation while remaining supportive.\n"
        )

    messages = [{"role": "system", "content": system_content}]

    for turn in conversation_history:
        role = turn.get("role")
        content = turn.get("content")

        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_message})

    return messages


def generate_reply(
    conversation_history: Sequence[Mapping[str, str]],
    user_message: str,
    knowledge_context: str = "",
    db: Session | None = None,
) -> str:
    """Generate an assistant reply using conversation history and retrieved context."""

    ai_settings = get_ai_runtime_settings(db)
    if not ai_settings["is_enabled"]:
        raise RuntimeError("AI responses are disabled by an administrator.")
    if not ai_settings["api_key"]:
        raise RuntimeError("The AI API key is not configured.")

    client = OpenAI(api_key=ai_settings["api_key"])

    response = client.chat.completions.create(
        model=ai_settings["model"],
        messages=build_prompt(
            conversation_history,
            user_message,
            knowledge_context,
        ),
    )

    if db is not None:
        _record_usage(db, response, ai_settings["model"])

    reply = response.choices[0].message.content

    if reply is None:
        raise RuntimeError("OpenAI returned an empty assistant reply.")

    return reply
