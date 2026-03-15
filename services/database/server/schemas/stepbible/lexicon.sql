
DROP SCHEMA lexicon CASCADE;
CREATE SCHEMA lexicon;

-- ==============================================================================================================================

CREATE TABLE IF NOT EXISTS lexicon.language(
    id          CHAR(1) PRIMARY KEY,
    name        TEXT,
    iso         CHAR(3),
    FOREIGN KEY (iso) REFERENCES standards.iso693_3_codes (id)
);
-- Language is A=Aramaic, H=Hebrew, G=Greek and N=Name (which is not language specific). 
INSERT INTO lexicon.language (id, name, iso)
VALUES
    ("A", "Aramaic" , "arc"),
    ("H", "Hebrew"  , "hbo"), -- Ancient Hebrew / 'heb' -> Modern Hebrew
    ("G", "Greek"   , "grc"),
    ("N", "Name"    , None);

CREATE TABLE IF NOT EXISTS lexicon.type(
    id          CHAR(1) PRIMARY KEY,
    name        TEXT
);
-- Type is A=Adjective, Adv=Adverb, Art=Article, Cond=Conditional, Conj=Conjunction, Cor=Correlative, DemP=Demonstrative Pn, ImpP=Impersonal Pn, Intg=Interogative, Intj=Interjection, N=Noun, Neg=Negative, Part=Particle, Prep=Preposition, PerP=Personal Pn, PosP=Possessive Pn, RefP=Reflexive Pn, RelP=Relative Pn, V=Verb. 
INSERT INTO lexicon.type (id, name)
VALUES
    ("A"    , "Adjective"),
    ("Adv"  , "Adverb"),
    ("Art"  , "Article"),
    ("Cond" , "Conditional"),
    ("Conj" , "Conjunction"),
    ("Cor"  , "Correlative"),
    ("DemP" , "Demonstrative Pn"),
    ("ImpP" , "Impersonal Pn"),
    ("Intg" , "Interogative"),
    ("Intj" , "Interjection"),
    ("N"    , "Noun"),
    ("Neg"  , "Negative"),
    ("Part" , "Particle"),
    ("Prep" , "Preposition"),
    ("PerP" , "Personal Pn"),
    ("PosP" , "Possessive Pn"),
    ("RefP" , "Reflexive Pn"),
    ("RelP" , "Relative Pn"),
    ("V"    , "Verb");

CREATE TABLE IF NOT EXISTS lexicon.gender(
    id          CHAR(1) PRIMARY KEY,
    name        TEXT
);
-- Gender is F=Female, M=Male, N=Neuter, C=Common and P or S is optionally added for Plural Singular
INSERT INTO lexicon.gender (id, name)
VALUES
    ("F", "Female"),
    ("M", "Male"), 
    ("N", "Neuter"),
    ("C", "Common"),
    ("P", "Plural"),
    ("S", "Singular");

CREATE TABLE IF NOT EXISTS lexicon.extra(
    id          CHAR(1) PRIMARY KEY,
    name        TEXT
);
-- Extra for Names is L=Location, P=Person, LG/PG=Gentilic, T=Title (i.e. any other capitalised nouns such as titles, months, gods, planets etc)
INSERT INTO lexicon.gender (id, name)
VALUES
    ("L"    , "Location"),
    ("P"    , "Person"),
    ("LG"   , "Gentilic"),
    ("PG"   , "Gentilic"),
    ("T"    , "Title");

CREATE TABLE IF NOT EXISTS lexicon.entry(
    id              CHAR(1) PRIMARY KEY,
    name            TEXT,
    description     TEXT
);
INSERT INTO lexicon.entry (id, name, description)
VALUES
    ("AS"   , "Abbott Smith",
        "from https://github.com/translatable-exegetical-tools/Abbott-Smith, with corrections and adapted by Tyndale Scholars. "),

    ("ML"   , "Middle Liddell",
        "from Perseus - used for Meaning in the Brief lexicon when there is no entry by (AS)"),

    ("LSJ"  , "Liddell-Scott-Jones",
        "from Perseus, with additional features and corrections by Tyndale House, Cambridge:
 - most abbreviations have been expanded, usually in accordance with the introductions to the lexicons but occasionally made clearer. 
 - dates have been added to authors by Tyndale House, using standard reference works. 
 - coding is added to hide bibliographic data under a link stating the earliest date included in that data. (Note, not all devices work well with tooltips, so consider implementing a clickable option such as http://jsfiddle.net/xaAN3/) ")

    ("MT"   , "Mounce's Teknia Greek dictionary",
        "from www.billmounce.com/greek-dictionary (with permission) -  used for Meaning in the Brief lexicon when there is no entry by (AS) or (ML)"),

    ("ABDB" , "Abridged BDB by Online Bible",
        "© Larry Pierce of OnlineBible.net <olbsupport@onlinebible.net>. They are for guidance only. Permission should be gained from Online Bible before these are applied in any project. "),

    -- OR BADG??? 
    ("BDB"  , "Brown–Driver–Briggs", 
        None),

    ("BADG" , "Bauer–Danker–Arndt–Gingrich",
        "")

    ("CLBL" , "J. Green's A Concise Lexicon of the Biblical Languages",
        "These definitions refer to J. Green's A Concise Lexicon of the Biblical Languages"),

    ("TWOT" , "Harris, Archer, & Waltke's Theological Wordbook of the Old Testament",
        "These definitions refer to Harris, Archer, & Waltke's Theological Wordbook of the Old Testament"),

    ("OPEN" , "OpenScripture's extended Strongs by Tyndale House Cambridge",
        "These have been edited to conform with OpenScripture's extended Strongs by Tyndale House Cambridge. Alignment with dStrongs is not yet completed. ")

-- ==============================================================================================================================

CREATE TABLE IF NOT EXISTS lexicon.tbesh(
    id                  SERIAL PRIMARY KEY,
    e_strong            TEXT,
    d_strong            TEXT,
    d_u_relationship    TEXT,
    u_strong            TEXT,
    iso                 TEXT,
    text                TEXT, -- Original Language -> Hebrew
    transliteration     TEXT,
    morph               TEXT,
    gloss               TEXT,
    meaning             TEXT
);

CREATE TABLE IF NOT EXISTS lexicon.tbesg(
    id                  SERIAL PRIMARY KEY,
    e_strong            TEXT,
    d_strong            TEXT,
    d_u_relationship    TEXT,
    u_strong            TEXT,
    iso                 TEXT,
    text                TEXT, -- Original Language -> Greek
    transliteration     TEXT,
    morph               TEXT,
    gloss               TEXT,
    meaning             TEXT,
    other_lexicon       TEXT, -- Abbot-Smith lexicon (AS), with gaps occassionally filled from edited versions of Middle LSJ
);

CREATE TABLE IF NOT EXISTS lexicon.tflsj(
    id                  SERIAL PRIMARY KEY,
    e_strong            TEXT,
    d_strong            TEXT,
    d_u_relationship    TEXT,
    u_strong            TEXT,
    iso                 TEXT,
    text                TEXT, -- Original Language -> Greek
    transliteration     TEXT,
    morph               TEXT,
    gloss               TEXT,
    meaning             TEXT    -- LSJ Meaning
);

-- ==============================================================================================================================

