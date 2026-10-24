from collections.abc import Mapping, Sequence

from openai import OpenAI

from app.config import settings

#prompt construction (tested successfully)
# python -c "from app.chat.llm import build_prompt; print(build_prompt([{'role': 'user', 'content': 'Hi'}, {'role': 'assistant', 'content': 'Hello!'}], 'How are you?'))"
# tested succesfully
SYSTEM_PROMPT = """You are a supportive mental health companion.
Respond with empathy, respect, and practical, nonjudgmental support.
Do not diagnose, prescribe treatment, or claim to replace a licensed
mental health professional. Encourage the user to seek professional support
when appropriate. If the user may be in immediate danger, encourage them to
contact local emergency services or a trusted person who can help right away."""


def build_prompt(
    conversation_history: Sequence[Mapping[str, str]],
    user_message: str,
) -> list[dict[str, str]]:
    """Build the OpenAI chat messages from prior turns and the current message."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for turn in conversation_history:
        role = turn.get("role")
        content = turn.get("content")
        if role not in {"user", "assistant"} or not isinstance(content, str):
            raise ValueError("Conversation history must contain user/assistant roles and string content.")
        messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_message})
    return messages

# LLM reply generation (tested successfully)
# python -c "from app.chat.llm import generate_reply; print(generate_reply([], 'I have been feeling stressed lately.'))"
# tested succesfully

def generate_reply(
    conversation_history: Sequence[Mapping[str, str]],
    user_message: str,
) -> str:
    """Generate an assistant reply using prior conversation turns."""
    client = OpenAI(api_key=settings.open_api_key)
    response = client.chat.completions.create(
        model=settings.openapi_model,
        messages=build_prompt(conversation_history, user_message),
    )

    reply = response.choices[0].message.content
    if reply is None:
        raise RuntimeError("OpenAI returned an empty assistant reply.")
    return reply
