from ingestor.stepbible.morphology.codes.feature_base import FeatureBase

class TenseCode(FeatureBase):
    # Format -> "Name": {"Codes": [""], "Description": ""}
    CODES       = "Codes"
    DESCRIPTION = "Description"

    values = {
        "": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Imperfect": {
            CODES           : ["I"],
            DESCRIPTION     : ""
        },
        "Perfect": {
            CODES           : ["R"],
            DESCRIPTION     : ""
        },
        "Pluperfect": {
            CODES           : ["L"],
            DESCRIPTION     : ""
        },
    }

    def __init__(self, manager, log, code):
        name        = "Case"
        description = ""
        limit       = 1
        union       = None

        super().__init__(manager, log, code, name, description, limit, union)

    # Past | Present | Future
    # Aorist | 
    # Imperfect | Perfect
    # Indefinite
    # Pluperfect
    # 

    # 2nd Perfect
    # 2nd Aorist
    # 2nd Future
    # Aorist
    # Imperfect
    # 2nd Pluperfect
    # indefinite tense
    # Perfect
    # Present
    # Pluperfect
    # Future
    # 2nd Present
    # Present/future
    # Past/present
    # Future/present