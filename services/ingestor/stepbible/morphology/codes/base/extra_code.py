
from ingestor.stepbible.morphology.codes.base_parser import BaseParser

class ExtraCode(BaseParser):
    # Numeral
    # Aeolic
    # Superlative
    # Abbreviated Numeral
    # Apocopated form
    # IRRegular or impure form
    # Transitive
    # Abbreviated
    # Interrogative
    # Negative
    # Comparative
    # Contracted form
    # Indeclinable Letter
    # Attic Greek form
    def __init__(self, manager, log, code):
        super().__init__(
            manager = manager, 
            log     = log, 
            code    = code
        )