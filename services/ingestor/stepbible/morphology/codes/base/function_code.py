from ingestor.stepbible.morphology.codes.feature_base import FeatureBase

class ExtraCode(FeatureBase):
    # Format -> "Name": {"Codes": [""], "Description": ""}
    CODES       = "Codes"
    DESCRIPTION = "Description"

    values = {
        "Relative Pronoun": {
            CODES           : ["R"],
            DESCRIPTION     : ""
        },
        "Conjunction": {
            CODES           : ["COND", "CONJ"],
            DESCRIPTION     : ""
        },
        "": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
        "": {
            CODES           : [""],
            DESCRIPTION     : ""
        },
    }

    def __init__(self, manager, log, code):
        name        = "Case"
        description = ""
        limit       = 1
        union       = None

        super().__init__(manager, log, code, name, description, limit, union)

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
