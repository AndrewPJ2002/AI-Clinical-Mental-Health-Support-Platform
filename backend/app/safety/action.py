from .rules import contains_crisis, usr_message_check


CRISIS_RESPONSE = """
I'm sorry you're going through this. You deserve support, and you don't have to face this alone.

If you may hurt yourself or someone else, or you're in immediate danger, call 911 or your local emergency number.

If you're in the United States and experiencing emotional distress or thoughts of suicide, call or text 988 to reach the Suicide & Crisis Lifeline, or visit 988lifeline.org to chat.

If possible, reach out to someone you trust and move to a safer place.
"""


def risk_response(text: str) -> dict:
    is_crisis = contains_crisis(text)
    red_flag = None

    if not is_crisis:
        red_flag = usr_message_check(text)

    is_high_risk = is_crisis or red_flag == "high"

    return {
        "is_crisis": is_high_risk,
        "risk_lvl": (
            "high"
            if is_high_risk
            else "medium"
            if red_flag == "medium"
            else "low"
        ),
        "source": "rules",
        "response": CRISIS_RESPONSE if is_high_risk else None,
    }


# ___Hardcoded test cases___
'''
message = "I want to kill myself"
result = risk_response(message)
print(
    f"Message: {message}\\n"
    f"Risk Level: {result['risk_lvl']}\\n"
    f"Is Crisis: {result['is_crisis']}\\n"
    f"Response: {result['response']}"
)

message1 = "I want to shoot this person"
result1 = risk_response(message1)
print(
    f"Message: {message1}\\n"
    f"Risk Level: {result1['risk_lvl']}\\n"
    f"Is Crisis: {result1['is_crisis']}\\n"
    f"Response: {result1['response']}"
)

message2 = "I have been so depressed lately"
result2 = risk_response(message2)
print(
    f"Message: {message2}\\n"
    f"Risk Level: {result2['risk_lvl']}\\n"
    f"Is Crisis: {result2['is_crisis']}\\n"
    f"Response: {result2['response']}"
)
'''

# NOTIFICATION TO THE THERAPIST CODE GOES HERE