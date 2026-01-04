
INSERT INTO bible.languages (iso, name, nameLocal, scriptDirection) VALUES 
    ('eng', 'English', 'English', 'LTR'),
    ('hbo', 'Hebrew, Ancient', 'עברית', 'RTL'),
    ('heb', 'Hebrew, Modern', 'עברית', 'RTL'),
    ('grc', 'Greek, Ancient', 'Ελληνιστική', 'LTR');
    -- ('', '', '', ''), 
    -- Probably need to add the following (from dbl website - check whether language codes differ) 
    --      [Greek: Ancient] [Ancient Greek (to 1453)] [Greek] [Hebrew] [Ancient Hebrew]
    -- Greek : https://app.library.bible/content?languageIsoCodes=ell%2Cgrc%2Cgrc%2Cgrc&sortBy=name&sortOrder=asc [33]
    -- Hebrew : https://app.library.bible/content?isOpenAccess=true&languageIsoCodes=heb%2Cheb&sortBy=name&sortOrder=asc [3]
    -- English : https://app.library.bible/content?languageIsoCodes=ang%2Cbzj%2Ceng%2Cgul%2Cicr%2Cjam%2Cjam%2Clir&sortBy=name&sortOrder=asc [176]
