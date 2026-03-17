
from ingestor.stepbible.morphology.codes.base_parser import BaseParser


class FunctionCode(BaseParser):
    # Adverb or adverb and particle combined
    # Possessive pronoun
    # Indeclinable Noun of Other type
    # Indeclinable Proper Noun
    # Interrogative pronoun
    # Correlative pronoun
    # Noun
    # Aramaic transliterated word
    # Interjection
    # Personal pronoun
    # Particle or Disjunctive
    # Interrogative Particle
    # Negative Particle
    # Demonstrative pronoun+Conjunction
    # Verb
    # Indefinite pronoun
    # Relative pronoun
    # Reciprocal pronoun
    # Correlative or Interrogative pronoun
    # Reflexive pronoun
    # Definite article
    # Adjective
    # Preposition
    # Suffix
    # Conjunction
    # Adverb
    # Demonstrative pronoun
    # Particle
    # Personal Pronoun
    # Punctuation
    # Relative Pronoun
    # Reciprocal Pronoun
    # Reflexive Pronoun
    # Correlative

    # Correlative or Interrogative
    # Possessive Pronoun
    # Article
    # Conditional
    # Pronoun
    # Demonstrative Pronoun
    # Indefinite Pronoun
    # Interogative
    # Negative
    def __init__(self, manager, log, code):
        super().__init__(
            manager = manager, 
            log     = log, 
            code    = code
        )
