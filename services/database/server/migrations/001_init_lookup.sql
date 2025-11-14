-- ================================================== Spacy Look up Tables ==================================================

INSERT INTO lookup.nlp_pos_types (pos_tag, description) 
VALUES
    ('ADJ',  'Adjective – modifies a noun (e.g. beautiful, large)'),
    ('ADP',  'Adposition – prepositions and postpositions (e.g. in, on, under)'),
    ('ADV',  'Adverb – modifies verbs, adjectives, or adverbs (e.g. quickly, very)'),
    ('AUX',  'Auxiliary verb – helps the main verb (e.g. is, have, will)'),
    ('CONJ', 'Conjunction – links words or clauses (e.g. and, or, but) [legacy tag]'),
    ('CCONJ','Coordinating conjunction – (e.g. and, but, or)'),
    ('SCONJ','Subordinating conjunction – introduces a clause (e.g. because, if, that)'),
    ('DET',  'Determiner – introduces a noun (e.g. the, a, this)'),
    ('INTJ', 'Interjection – emotion words (e.g. oh, wow, hey)'),
    ('NOUN', 'Noun – person, place, thing, concept'),
    ('PROPN','Proper noun – specific name (e.g. Jesus, Jerusalem)'),
    ('NUM',  'Numeral – expresses a number (e.g. one, first)'),
    ('PART', 'Particle – function word (e.g. not, to in "to go")'),
    ('PRON', 'Pronoun – replaces a noun (e.g. he, they, which)'),
    ('PUNCT','Punctuation – symbols like . , ! ?'),
    ('SYM',  'Symbol – special symbols or emojis'),
    ('VERB','Verb – action or state (e.g. run, is)'),
    ('X',    'Other – foreign words, errors, or unknown tokens'),
    ('SPACE','Space – whitespace characters');

INSERT INTO lookup.nlp_tag_types (tag, description) 
VALUES
    -- Nouns
    ('NN',  'Noun, singular or mass'),
    ('NNS', 'Noun, plural'),
    ('NNP', 'Proper noun, singular'),
    ('NNPS','Proper noun, plural'),

    -- Pronouns
    ('PRP',  'Personal pronoun (I, you, he)'),
    ('PRP$', 'Possessive pronoun (my, your, his)'),
    ('WP',   'Wh-pronoun (who, what)'),
    ('WP$',  'Possessive wh-pronoun (whose)'),

    -- Verbs
    ('VB',  'Verb, base form'),
    ('VBD', 'Verb, past tense'),
    ('VBG', 'Verb, gerund/present participle'),
    ('VBN', 'Verb, past participle'),
    ('VBP', 'Verb, non-3rd person singular present'),
    ('VBZ', 'Verb, 3rd person singular present'),
    ('MD',  'Modal verb (can, will, must)'),

    -- Adjectives
    ('JJ',   'Adjective'),
    ('JJR',  'Adjective, comparative'),
    ('JJS',  'Adjective, superlative'),

    -- Adverbs
    ('RB',   'Adverb'),
    ('RBR',  'Adverb, comparative'),
    ('RBS',  'Adverb, superlative'),
    ('WRB',  'Wh-adverb (where, when, how)'),

    -- Determiners & Articles
    ('DT',  'Determiner (the, a, this)'),
    ('PDT', 'Predeterminer (all, half)'),
    ('WDT', 'Wh-determiner (which, whatever)'),

    -- Conjunctions & Particles
    ('CC',  'Coordinating conjunction (and, but)'),
    ('IN',  'Preposition or subordinating conjunction'),
    ('TO',  'Particle “to” (to go)'),
    ('RP',  'Particle (up, off, over)'),

    -- Numerals
    ('CD', 'Cardinal number'),

    -- Others
    ('EX', 'Existential there (there is...)'),
    ('FW', 'Foreign word'),
    ('LS', 'List item marker (1., A.)'),
    ('SYM','Symbol'),
    ('UH', 'Interjection'),
    ('.',  'Punctuation');

INSERT INTO lookup.nlp_dep_types (dep, description) 
VALUES
    ('acl',    'Clausal modifier of noun'),
    ('acomp',  'Adjectival complement'),
    ('advcl',  'Adverbial clause modifier'),
    ('advmod', 'Adverbial modifier'),
    ('agent',  'Agent in passive'),
    ('amod',   'Adjectival modifier'),
    ('appos',  'Appositional modifier'),
    ('aux',    'Auxiliary'),
    ('auxpass','Passive auxiliary'),
    ('case',   'Case marking for noun'),
    ('cc',     'Coordinating conjunction'),
    ('ccomp',  'Clausal complement'),
    ('compound','Compound noun modifier'),
    ('conj',   'Conjunct'),
    ('cop',    'Copula (linking verb)'),
    ('csubj',  'Clausal subject'),
    ('dep',    'Unspecified dependency'),
    ('det',    'Determiner'),
    ('dobj',   'Direct object'),
    ('expl',   'Expletive “there”, “it”'),
    ('fixed',  'Fixed multiword expression'),
    ('flat',   'Names / flat structures'),
    ('iobj',   'Indirect object'),
    ('mark',   'Subordinating conjunction'),
    ('nmod',   'Nominal modifier'),
    ('nsubj',  'Nominal subject'),
    ('nsubjpass','Passive subject'),
    ('nounmod','Noun modifier'),
    ('npadvmod','Noun phrase as adverbial'),
    ('num',    'Numeric modifier'),
    ('obj',    'Object'),
    ('obl',    'Oblique nominal'),
    ('oprd',   'Object predicate'),
    ('parataxis','Side-by-side clause'),
    ('pcomp',  'Complement of preposition'),
    ('pobj',   'Object of preposition'),
    ('poss',   'Possession modifier'),
    ('preconj','Pre-correlative conjunction'),
    ('predet', 'Predeterminer'),
    ('prep',   'Prepositional modifier'),
    ('prt',    'Particle'),
    ('punct',  'Punctuation'),
    ('quantmod','Quantifier modifier'),
    ('relcl',  'Relative clause'),
    ('root',   'Root of sentence'),
    ('xcomp',  'Open clausal complement');

-- ================================================== Node Look up Tables ==================================================

INSERT INTO lookup.node_attributes (attribute, description, active) 
VALUES
    ("code","book code for this book usx file", TRUE),
    ("sid","Marks start of verse or chapter with reference", TRUE),
    ("eid","Marks end of verse or chapter with reference", TRUE),
    ("vid","Marks continuation of verse in a paragraph with reference", TRUE),
    ("style","styling info", TRUE),
    ("number","Chapter or Verse number", TRUE),
    ("caller","", TRUE),
    ("closed","", TRUE),
    ("version","usx or xml version used", TRUE),
    ("strong","Strong's number of Hebrew or Greek for particular word", TRUE),
    ("loc","reference to chapter or verse (could include spread)", TRUE),
    ("encoding","text encoding for the file", TRUE);

INSERT INTO lookup.node_types (node, description, active) 
VALUES
    ("xml","tag representing xml format", TRUE),
    ("usx","tag representing usx format, encapsulating all its content", TRUE),
    ("para","tag representing a paragraph (each new para is a new line, so doesn't match logical paragraph structure e.g. in poetry)", TRUE),
    ("chapter","tag representing a chapter", TRUE),
    ("verse","tag representing a verse", TRUE),
    ("char","tag representing a note, extra info or strongs", TRUE),
    ("ref","tag representing a reference to other parts of scripture", TRUE),
    ("note","tag representing a footnote or crossreference", TRUE),
    ("book","tag representing a book", TRUE),
    ("text","not a tag but represents text in the parsed xml structure", TRUE);

INSERT INTO lookup.node_map (node_type, node_attribute) 
VALUES
    ("","");

-- ================================================== Quote Look up Tables ==================================================

INSERT INTO lookup.quote_attribution_types (attribution, type, description) 
VALUES
    ("speaker", NULL, "The person saying this"),
    ("audience", NULL, "This is being spoken to"),
    ("narrative", NULL, "This is narrative and therefore not got a certain speaker, just a character it represents"),
    ("quoting", NULL, "If this is quoting someone else's speach (scripture cross reference)");

-- ================================================== Entity Look up Tables ==================================================

-- INSERT INTO lookup.entity_relationship_types (relationship_types, description) 
-- VALUES
--     ();

-- INSERT INTO lookup.entity_relationship_map (relationship, rtl) 
-- VALUES
--     ();

-- ================================================== Other Look up Tables ==================================================

-- INSERT INTO lookup.word_tags (name, description) 
-- VALUES
--     ();