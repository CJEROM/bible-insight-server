from ingestor.stepbible.morphology.codes.feature_base import FeatureBase

class CaseCode(FeatureBase):
    # Format -> "Name": {"Codes": [""], "Description": ""}
    CODES       = "Codes"
    DESCRIPTION = "Description"

    values = {
        "Accusative": {
            CODES           : ["A"],
            DESCRIPTION     : ""
        },
        "Dative": {
            CODES           : ["D"],
            DESCRIPTION     : ""
        },
        "Genitive": {
            CODES           : ["G"],
            DESCRIPTION     : ""
        },
        "Nominative": {
            CODES           : ["N"],
            DESCRIPTION     : ""
        },
        "Vocative": {
            CODES           : ["V"],
            DESCRIPTION     : ""
        }
    }

    def __init__(self, manager, log, code):
        name        = "Case"
        description = ""
        limit       = 1
        union       = None

        super().__init__(manager, log, code, name, description, limit, union)