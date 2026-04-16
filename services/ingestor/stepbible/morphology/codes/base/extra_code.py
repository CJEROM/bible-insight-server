from ingestor.stepbible.morphology.codes.feature_base import FeatureBase

class ExtraCode(FeatureBase):
    # Format -> "Name": {"Codes": [""], "Description": ""}
    CODES       = "Codes"
    DESCRIPTION = "Description"

    values = {
        # ------------------------------------ Special Types ------------------------------------
        "Numeral": {
            CODES: ["NUI"],
            DESCRIPTION: "Indicates a numerical form (number word), such as cardinal or ordinal numbers."
        },
        "Indeclinable Letter": {
            CODES: ["LI"],
            DESCRIPTION: "A letter or symbol that does not change form (not declined or inflected)."
        },
        # ------------------------------------ Degree ------------------------------------
        "Superlative": {
            CODES: ["S"],
            DESCRIPTION: "Expresses the highest or most extreme degree of a quality (e.g., 'greatest', 'highest')."
        },
        "Comparative": {
            CODES: ["C", "K"],
            DESCRIPTION: "Expresses a higher degree of comparison between two things (e.g., 'greater', 'more')."
        },
        # ------------------------------------ Form changes ------------------------------------
        "Contracted form": {
            CODES: ["C"],
            DESCRIPTION: "A form where vowels have been contracted (merged), common in Greek verb forms."
        },
        "Abbreviated": {
            CODES: ["ABB"],
            DESCRIPTION: "Indicates a shortened or abbreviated form of a word."
        },
        "Apocopated form": {
            CODES: ["AP"],
            DESCRIPTION: "A shortened form where the ending of a word has been dropped."
        },
        "Irregular or impure form": {
            CODES: ["IRR"],
            DESCRIPTION: "A form that does not follow standard grammatical patterns or expected inflection rules."
        },
        # ------------------------------------ Syntax/Function ------------------------------------
        "Transitive": {
            CODES: ["T"],
            DESCRIPTION: "Indicates that a verb takes a direct object (the action is performed on something)."
        },
        "Interrogative": {
            CODES: ["I"],
            DESCRIPTION: "Marks a word used to ask a question (e.g., 'who?', 'what?', 'why?')."
        },
        "Negative": {
            CODES: ["N"],
            DESCRIPTION: "Indicates negation, expressing 'not' or denial."
        },
        # ------------------------------------ Dialect ------------------------------------
        "Attic Greek form": {
            CODES: ["ATT"],
            DESCRIPTION: "Marks a form characteristic of the Attic dialect of Greek, often differing from Koine usage."
        },
        "Aeolic": {
            CODES: ["A"],
            DESCRIPTION: "Marks a form belonging to the Aeolic dialect of Greek, which may differ in spelling or form from standard Koine."
        },
        # "Indeclinable": {
        #     CODES           : ["I"],
        #     DESCRIPTION     : ""
        # },
        # "Letter": {
        #     CODES           : ["L"],
        #     DESCRIPTION     : ""
        # },
    }

    def __init__(self, manager, log, code):
        name        = "Extra"
        description = (
            "Additional grammatical or linguistic markers that provide extra information about a word’s form, "
            "usage, dialect, or degree beyond standard morphological features."
        )
        limit       = 2
        union       = None

        super().__init__(manager, log, code, name, description, limit, union)

    # Numeral
    # Aeolic
    # Superlative
    # Abbreviated Numeral
    # Apocopated form
    # IRRegular or impure form
    # Transitive
    # Abbreviated
    # Interrogative
    # Negative
    # Comparative
    # Contracted form
    # Indeclinable Letter
    # Attic Greek form