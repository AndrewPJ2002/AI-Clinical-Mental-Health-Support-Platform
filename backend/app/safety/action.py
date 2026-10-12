from app.safety.rules import contains_crisis

CRISIS_RESPONSE = """
I am ectremely sorry to hear what you are going through, and you are not alone.

If you are in immediate danger or thinking about harming yourself, please contact
(EMERGENCY NUMBER) or a (ANCHORED_SUPPORT_SERVICES_LINE). If you can, reach out
to someone you trust and stay somewhere safe.

"""

# TBD later: add more nuanced risk levels based on the severity of the crisis words detected
def risk_lvl(text:str) -> dict:
    is_crisis = contains_crisis(text)
    return {
        "is_crisis": is_crisis,
        "risk_lvl": "high" if is_crisis else "low",
        "source": "rules",
    }