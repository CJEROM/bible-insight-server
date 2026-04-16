from ingestor.stepbible.morphology.codes.feature_base import FeatureBase

class ExtraCode(FeatureBase):
    # Format -> "Name": {"Codes": [""], "Description": ""}
    CODES       = "Codes"
    DESCRIPTION = "Description"

    values = {
        "": {
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

    # Gentilic
    # Person name Transcribed from Aramaic
    # Person Gentilic

    # Type
    # Individual
    # Title Gentilic
    # Location Gentilic
    # Individual Gentilic
    # Title
    # Location
    # Person