
from ingestor.stepbible.morphology.codes.base_parser import BaseParser

class NumberCode(BaseParser):
    # Singular  (S / s) 
    # Plural    (P / p) 
    # Dual      (D / d)???
    def __init__(self, manager, log, code):
        super().__init__(
            manager = manager, 
            log     = log, 
            code    = code
        )