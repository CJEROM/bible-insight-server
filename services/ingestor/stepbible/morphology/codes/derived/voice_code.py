
from ingestor.stepbible.morphology.codes.base_parser import BaseParser

class VoiceCode(BaseParser):
    # impersonal active
    # Middle or Passive Deponent
    # Passive
    # Active
    # Middle
    # Passive Deponent
    # indefinite voice
    # Middle Deponent
    # Middle or Passive
    # Reflexive/iterative
    def __init__(self, manager, log, code):
        super().__init__(
            manager = manager, 
            log     = log, 
            code    = code
        )