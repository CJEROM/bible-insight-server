INSERT INTO bible.dblinfo (dbl_id, agreement_id) VALUES
    -- TEXT Medium Translations
    ('65eec8e0b60e656b', 246069), -- FBV | text | Free Bible Version
    ('de4e12af7f28f599', 245514), -- KJV | text | King James (Authorised) Version
    ('55212e3cf5d04d49', 253126), -- KJVCPB | text | Cambridge Paragraph Bible of the KJV
    ('66c22495370cdfc0', 246913), -- T4T | text | Translation for Translators
    ('6bab4d6c61b31b80', 252265), -- LXXup | text | Brenton English Septuagint (Updated Spelling and Formatting)
    ('32664dc3288a28df', 265137), -- WEBUS | text | World English Bible, American English Edition, without Strong's Numbers
    ('7142879509583d59', 240016), -- WEBBE | text | World English Bible British Edition
    ('01b29f4b342acc35', 260328), -- LSV | text | Literal Standard Version
    ('f72b840c855f362c', 240017), -- WMB | text | World Messianic Bible
    ('01b29f4b342acc35', 254051), -- LSV | text | Literal Standard Version
    ('65bfdebd704a8324', 250819), -- Brenton | text | Brenton English translation of the Septuagint
    ('40072c4a5aba4022', 240019), -- RV | text | Revised Version 1885
    ('06125adad2d5898a', 240014), -- ASV | text | The Holy Bible, American Standard Version
    ('04da588535d2f823', 240018), -- WMBBE | text | World Messianic Bible British Edition
    ('65eec8e0b60e656b', 262699), -- FBV | text | Free Bible Version
    ('72f4e6dc683324df', 278101), -- WEBU | text | World English Bible Updated
    ('55ec700d9e0d77ea', 252280), -- EMTV | text | English Majority Text Version
    ('179568874c45066f', 245511), -- DRA | text | Douay-Rheims American 1899
    ('2f0fd81d7b85b923', 253125), -- F35 | text | The English New Testament According to Family 35
    ('9879dbb7cfe39e4d', 240020), -- WEB | text | World English Bible
    ('bba9f40183526463', 259557), -- BSB | text | Berean Standard Bible
    ('7142879509583d59', 242201), -- WEBBE | text | World English Bible British Edition
    ('32339cf2f720ff8e', 265856), -- TCENT | text | The Text-Critical English New Testament
    ('901dcd9744e1bf69', 259032), -- BYZ1904 | text | 1904 Patriarchal Greek New Testament with 20 corrections from later editions
    ('7644de2e4c5188e5', 265855), -- TCGNT | text | Text-Critical Greek New Testament
    ('47f396bad37936f0', 269494), -- SRGNT | text | Solid Rock Greek New Testament
    ('5e29945cf530b0f6', 253124), -- F35 | text | The Greek New Testament According to Family 35
    ('c114c33098c4fef1', 252266), -- GRCBRENT | text | Brenton Greek Septuagint
    ('3aefb10641485092', 252238), -- GRCTR | text | Greek Textus Receptus
    ('0b262f1ed7f084a6', 270964), -- WLC | text | The Hebrew Bible, Westminister Leningrad Codex
    ('a8a97eebae3c98e4', 261769); -- HDZP | text | BiblicaÂ® Open Hebrew Living New Testament 2009
    -- Audio Medium Translations
    -- ('',  ); --  | audio |

INSERT INTO bible.dblinfo (dbl_id, agreement_id, supported, reason_not_supported) VALUES
    ('ec290b5045ff54a5', 252291, FALSE, 'Not Valid -> Flawed USX files'), -- OKE | text | Targum Onkelos Etheridge
    ('c89622d31b60c444', 272278, FALSE, 'Redundant -> introduces too much noise and not for our spec'); -- TOJB2011 | text | The Orthodox Jewish Bible