#red_flag detection

# rule-based approach
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
    "hurt myself", "hurting myself", "harm myself", "harming myself", "self harm",
    "self-harm", "selfharm", "cut myself", "cutting myself", "self-injury",
    "self injury", "self-injure", "self injure",

    # referencing plans
    "suicide plan", "suicide note", "goodbye note", "final goodbye",
    "saying goodbye to everyone", "giving away my things",
    "won't be around much longer", "this is my last day", "i want to disappear forever",

    # slang, informal expressions
    "unalive", "unalive myself", "kms", "kys", "k1ll",
    "sewerslide", "sui", "s*icide", "su1cide"

]

def contains_crisis(text: str) -> bool:
    lowered_text = text.lower()
    return any(word in lowered_text for word in CRISIS_DICT)


# ML based apprach goes here TBD