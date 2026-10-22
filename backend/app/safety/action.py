from .rules import contains_crisis, usr_message_check

CRISIS_RESPONSE = """
I am extremely sorry to hear what you are going through, and you are not alone.

If you are in immediate danger or thinking about harming yourself, please contact
(EMERGENCY NUMBER) or a (ANCHORED_SUPPORT_SERVICES_LINE). If you can, reach out
to someone you trust and stay somewhere safe.

"""

def risk_response(text:str) -> dict:
    is_crisis = contains_crisis(text)
    red_flag = None if is_crisis else usr_message_check(text)
    is_high_risk = is_crisis or red_flag == "high"

    return {
        "is_crisis": is_high_risk,
        "risk_lvl": (
            "high" if is_high_risk
            else "medium" if red_flag == "medium"
            else "low"
        ),
        "source": "rules",
        "response": CRISIS_RESPONSE if is_high_risk else None,
    }


#___Hardcoded test cases___
'''
message = "I want to kill myself"
result = risk_response(message)
print(f"Message: {message}\nRisk Level: {result['risk_lvl']}\nIs Crisis: {result['is_crisis']}\nResponse: {result['response']}")

message1 = "I want to shoot this person"
result1 = risk_response(message1)
print(f"Message: {message1}\nRisk Level: {result1['risk_lvl']}\nIs Crisis: {result1['is_crisis']}\nResponse: {result1['response']}")

message2 = "I have been so depressed lately"
result2 = risk_response(message2)
print(f"Message: {message2}\nRisk Level: {result2['risk_lvl']}\nIs Crisis: {result2['is_crisis']}\nResponse: {result2['response']}")

'''

#NOTIFICATION TO THE THERAPIST CODE GOES HERE