
from ingestor.stepbible.morphology.codes.base_parser import BaseParser

class NameTypeCode(BaseParser):
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
    def __init__(self, manager, log, code):
        super().__init__(
            manager = manager, 
            log     = log, 
            code    = code
        )