
from ingestor.stepbible.morphology.codes.base_parser import BaseParser

class GreekCode(BaseParser):
    # Code Completely in Capitals 
    def __init__(self, manager, log, code):
        super().__init__(
            manager = manager, 
            log     = log, 
            code    = code
        )