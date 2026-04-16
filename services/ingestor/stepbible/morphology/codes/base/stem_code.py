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

    # Peil
    # Peal
    # Qal
    # Shaphel
    # Haphel
    # Ishtaphel
    # Hishtaphel
    # Hithpael
    # Aphel
    # Hitpaal
    # Tiphil
    # Piel
    # Nithpael
    # Pual
    # Niphal
    # Hiphil
    # Polal
    # Hothpaal
    # Hophal
    # Hitpael
    # Pael
    # Hitpeel