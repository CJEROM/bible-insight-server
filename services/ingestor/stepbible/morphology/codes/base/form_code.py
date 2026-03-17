
from ingestor.stepbible.morphology.codes.base_parser import BaseParser

class FormCode(BaseParser):
    # Interrogative
    # Definite
    # Definite article (Aramaic)
    # Common
    # Directional
    # Consecutive
    # Infinitive
    # Participle
    # Paragogic Hé
    # Paragogic Nun
    # Conditional
    # Definite article (Hebrew)
    # Interjection
    # Demonstrative
    # Negative
    # Object indicator
    # Relative
    # Imperfect
    # Imperative
    # Perfect
    # Gentilic
    # Proper
    # Consecutive Imperfect
    # Title
    # Numerical
    # Consecutive Perfect
    # Personal
    # Participle passive
    # Numerical position
    # Conjunction+Imperfect
    def __init__(self, manager, log, code):
        super().__init__(
            manager = manager, 
            log     = log, 
            code    = code
        )