
from ingestor.stepbible.morphology.codes.base_parser import BaseParser

class MoodCode(BaseParser):
    # Subjunctive
    # Imperative
    # jussive
    # Optative
    # Indicative
    # Indicative/jussive
    # Cohortative
    # Indicative/cohortative
    # Jussive
    def __init__(self, manager, log, code):
        super().__init__(
            manager = manager, 
            log     = log, 
            code    = code
        )

