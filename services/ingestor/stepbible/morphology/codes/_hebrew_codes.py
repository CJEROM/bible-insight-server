
from ingestor.stepbible.morphology.codes.base_parser import BaseParser

class HebrewCode(BaseParser):
    # Code has MAX 2 capitals in entire string
    def __init__(self, manager, log, code):
        super().__init__(
            manager = manager, 
            log     = log, 
            code    = code
        )