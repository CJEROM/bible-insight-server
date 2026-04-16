
from ingestor.stepbible.morphology.codes.base_parser import BaseParser

from manager.managerhandler import ManagerHandler
from manager.logmanager import LogManager

class FeatureBase(BaseParser):
    # Format -> "Name": {"Codes": [""], "Description": ""}
    CODES       = "Codes"
    DESCRIPTION = "Description"

    values = {
        "Example": {
            CODES           : [""],
            DESCRIPTION     : ""
        }
    }

    def __init__(self, 
            manager     : ManagerHandler, 
            log         : LogManager, 
            code        : str,
            name        : str,
            subtype     : str,
            description : str,
            limit       : int,
            union       : str,
        ):
        super().__init__(
            manager = manager, 
            log     = log, 
            code    = code
        )

        self.feature_name           = name
        self.subtype                = subtype
        self.feature_description    = description
        self.feature_limit          = limit
        self.feature_union          = union

        self.feature_id             = self.init_feature()

        self.init_feature_values()

    def init_feature(self):
        feature_id = self.write.write_morphology_features(
            name        = self.feature_name,
            subtype     = self.subtype,
            description = self.feature_description,
            limit       = self.feature_limit,       # Can only have 1 assigned
            union       = self.feature_union        # We should ignore any that go over the limit
        )
        return feature_id

    def init_feature_values(self):
        for name, data in self.values.items():
            value_name          = name
            value_description   = data.get(self.DESCRIPTION)

            self.write.write_morphology_feature_value(
                feature_id  = self.feature_id,
                value       = value_name,
                description = value_description
            )

class FeatureBaseMapping():
    pass

class FeatureBaseRules():
    pass