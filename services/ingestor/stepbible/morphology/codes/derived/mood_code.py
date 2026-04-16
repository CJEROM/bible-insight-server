from ingestor.stepbible.morphology.codes.feature_base import FeatureBase

# NOT Always just a derived feature

class MoodCode(FeatureBase):
    # Format -> "Name": {"Codes": [""], "Description": ""}
    CODES       = "Codes"
    DESCRIPTION = "Description"

    values = {
        "Subjunctive": {
            CODES           : ["S"],
            DESCRIPTION     : ""
        },
        "Imperative": {
            CODES           : ["M", "v"],
            DESCRIPTION     : ""
        },
        "Optative": {
            CODES           : ["O"],
            DESCRIPTION     : ""
        },
        "Jussive": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Indicative": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "Cohortative": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
    }

    def __init__(self, manager, log, code):
        name        = "Mood"
        description = ""
        limit       = 1
        union       = None

        super().__init__(manager, log, code, name, description, limit, union)

    # Subjunctive
    # Imperative
    # jussive
    # Optative
    # Indicative
    # Indicative/jussive
    # Cohortative
    # Indicative/cohortative
    # Jussive