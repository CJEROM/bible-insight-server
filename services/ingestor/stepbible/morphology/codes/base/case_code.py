
from ingestor.stepbible.morphology.codes.base_parser import BaseParser

class CaseCode(BaseParser):
    # Vocative
    # Nominative
    # Dative
    # Accusative
    # Genitive
    def __init__(self, manager, log, code):
        super().__init__(
            manager = manager, 
            log     = log, 
            code    = code
        )