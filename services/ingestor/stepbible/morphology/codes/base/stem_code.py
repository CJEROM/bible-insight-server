
from ingestor.stepbible.morphology.codes.base_parser import BaseParser

class StemCode(BaseParser):
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
    def __init__(self, manager, log, code):
        super().__init__(
            manager = manager, 
            log     = log, 
            code    = code
        )