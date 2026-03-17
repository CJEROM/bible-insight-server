
from ingestor.stepbible.morphology.codes.base_parser import BaseParser

class ActionCode(BaseParser):
    # Simple
    # Causative/declarative
    # Intensive/resultive/transtive
    def __init__(self, manager, log, code):
        super().__init__(
            manager = manager, 
            log     = log, 
            code    = code
        )