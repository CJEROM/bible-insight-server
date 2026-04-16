from ingestor.stepbible.morphology.codes.feature_base import FeatureBase

class FormCode(FeatureBase):
    # Format -> "Name": {"Codes": [""], "Description": ""}
    CODES       = "Codes"
    DESCRIPTION = "Description"

    values = {
        # ------------------------------------ VerbForm ------------------------------------
        "Infinitive": { 
            CODES           : [""], # RAN
            DESCRIPTION     : ""
        },
        "Participle": {
            CODES           : ["P"],
            DESCRIPTION     : ""
        },
        # ------------------------------------ Tense ------------------------------------
        "Imperfect": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        # ------------------------------------ Mood ------------------------------------
        "Imperative": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        # ------------------------------------ SyntaxRole ------------------------------------
        "Relative": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Conjunction": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        # ------------------------------------ NounType ------------------------------------
        "Common": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Gentilic": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Proper": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        # ------------------------------------ HebrewForm ------------------------------------
        "Consecutive": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Paragogic Hé": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Paragogic Nun": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        # ------------------------------------ OTHER ------------------------------------
        "Interrogative": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Definite": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Definite article (Aramaic)": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Definite article (Hebrew)": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Directional": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Conditional": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Interjection": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Demonstrative": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Negative": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Object indicator": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Numerical": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Numerical position": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Personal": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Participle passive": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
    }

    def __init__(self, manager, log, code):
        name        = "Form"
        description = ""
        limit       = 1
        union       = None

        super().__init__(manager, log, code, name, description, limit, union)

    # Interrogative
    # Definite
    # Definite article (Aramaic)
    # Common
    # Directional
    # Consecutive
    # Infinitive
    # Participle
    # Paragogic Hé
    # Paragogic Nun
    # Conditional
    # Definite article (Hebrew)
    # Interjection
    # Demonstrative
    # Negative
    # Object indicator
    # Relative
    # Imperfect
    # Imperative
    # Perfect
    # Gentilic
    # Proper
    # Consecutive Imperfect
    # Title
    # Numerical
    # Consecutive Perfect
    # Personal
    # Participle passive
    # Numerical position
    # Conjunction+Imperfect