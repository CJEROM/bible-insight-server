from ingestor.stepbible.morphology.codes.feature_base import FeatureBase

class ExtraCode(FeatureBase):
    # Format -> "Name": {"Codes": [""], "Description": ""}
    CODES       = "Codes"
    DESCRIPTION = "Description"

    values = {
        "Simple": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Causative": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Declarative": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Intensive": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Resultive": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Transtive": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Causative/declarative": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Intensive/resultive/transtive": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
    }

    def __init__(self, manager, log, code):
        name        = "Case"
        description = ""
        limit       = 1
        union       = None

        super().__init__(manager, log, code, name, description, limit, union)

    # Simple
    # Causative/declarative
    # Intensive/resultive/transtive