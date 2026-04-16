from ingestor.stepbible.morphology.codes.feature_base import FeatureBase

class ExtraCode(FeatureBase):
    # Format -> "Name": {"Codes": [""], "Description": ""}
    CODES       = "Codes"
    DESCRIPTION = "Description"

    values = {
        "Passive": {
            CODES           : ["P"],
            DESCRIPTION     : ""
        },
        "Active": {
            CODES           : ["A"],
            DESCRIPTION     : ""
        },
        "Middle": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Reflexive/iterative": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Impersonal": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Deponent": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Middle or Passive Deponent": {
            CODES           : ["N"],
            DESCRIPTION     : ""
        },
    }

    def __init__(self, manager, log, code):
        name        = "Case"
        description = ""
        limit       = 1
        union       = None

        super().__init__(manager, log, code, name, description, limit, union)

    # impersonal active
    # Middle or Passive Deponent
    # Passive
    # Active
    # Middle
    # Passive Deponent
    # indefinite voice
    # Middle Deponent
    # Middle or Passive
    # Reflexive/iterative