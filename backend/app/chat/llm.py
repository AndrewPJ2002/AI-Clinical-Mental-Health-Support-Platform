from typing import Mapping, Sequence

from openai import OpenAI

from app.config import settings


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
) -> str:
    """Generate an assistant reply using conversation history and retrieved context."""

    client = OpenAI(api_key=settings.open_api_key)

    response = client.chat.completions.create(
        model=settings.openapi_model,
        messages=build_prompt(
            conversation_history,
            user_message,
            knowledge_context,
        ),
    )

    reply = response.choices[0].message.content

    if reply is None:
        raise RuntimeError("OpenAI returned an empty assistant reply.")

    return reply