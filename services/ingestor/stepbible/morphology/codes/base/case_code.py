from ingestor.stepbible.morphology.codes.feature_base import FeatureBase

class CaseCode(FeatureBase):
    # Format -> "Name": {"Codes": [""], "Description": ""}
    CODES       = "Codes"
    DESCRIPTION = "Description"

    values = {
        "Accusative": {
            CODES: ["A"],
            DESCRIPTION: "Marks the direct object of a verb or the target of an action. Answers 'whom?' or 'what?'."
        },
        "Dative": {
            CODES: ["D"],
            DESCRIPTION: "Indicates the indirect object, recipient, or beneficiary of an action. Often translated as 'to' or 'for'."
        },
        "Genitive": {
            CODES: ["G"],
            DESCRIPTION: "Expresses possession, origin, relationship, or description. Often translated as 'of'."
        },
        "Nominative": {
            CODES: ["N"],
            DESCRIPTION: "Marks the subject of a sentence—the one performing or being described by the verb."
        },
        "Vocative": {
            CODES: ["V"],
            DESCRIPTION: "Used for direct address, calling or speaking to someone."
        }
    }

    def __init__(self, manager, log, code):
        name        = "Case"
        description = (
            "Grammatical case indicates the role a noun or pronoun plays in a sentence, "
            "such as subject, object, possession, or address."
        )
        limit       = 1
        union       = None

        super().__init__(manager, log, code, name, description, limit, union)