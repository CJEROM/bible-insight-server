
from ingestor.stepbible.morphology.codes.base_parser import BaseParser

class TenseCode(BaseParser):
    # Past | Present | Future
    # Aorist | 
    # Imperfect | Perfect
    # Indefinite
    # Pluperfect
    # 

    # 2nd Perfect
    # 2nd Aorist
    # 2nd Future
    # Aorist
    # Imperfect
    # 2nd Pluperfect
    # indefinite tense
    # Perfect
    # Present
    # Pluperfect
    # Future
    # 2nd Present
    # Present/future
    # Past/present
    # Future/present
    def __init__(self, manager, log, code):
        super().__init__(
            manager = manager, 
            log     = log, 
            code    = code
        )