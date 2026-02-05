-- ============================================================================
-- 1. LICENCE ATTRIBUTES
-- ============================================================================

INSERT INTO audit.licence_attributes (attribute_code, name, description, attribute_type)
VALUES 
    -- ============================================================================
    -- PERMISSIONS: What you CAN do
    -- ============================================================================
    ('COMMERCIAL', 'Commercial Use', 'May use for commercial purposes', 'PERMISSION'),
    ('DISTRIBUTE', 'Distribution', 'May distribute copies', 'PERMISSION'),
    ('MODIFY', 'Modification', 'May modify or create derivatives', 'PERMISSION'),
    ('TRANSLATE', 'Translation', 'May translate to other languages', 'PERMISSION'),
    ('PRINT', 'Print/Physical', 'May create printed/physical copies', 'PERMISSION'),
    ('DIGITAL', 'Digital Distribution', 'May distribute digitally', 'PERMISSION'),
    ('AUDIO', 'Audio Production', 'May create audio versions', 'PERMISSION'),
    ('VIDEO', 'Video Production', 'May create video versions', 'PERMISSION'),
    ('SUBLICENSE', 'Sublicensing', 'May grant rights to others', 'PERMISSION'),
    ('PRIVATE_USE', 'Private Use', 'May use privately/internally', 'PERMISSION'),
    
    -- ============================================================================
    -- OBLIGATIONS: What you MUST do
    -- ============================================================================
    ('ATTRIBUTION', 'Attribution Required', 'Must credit the creator/source', 'OBLIGATION'),
    ('SHARE_ALIKE', 'Share Alike', 'Derivatives must use same license', 'OBLIGATION'),
    ('NOTICE', 'License Notice', 'Must include copy of license', 'OBLIGATION'),
    ('STATE_CHANGES', 'State Changes', 'Must document modifications made', 'OBLIGATION'),
    ('DISCLOSE_SOURCE', 'Disclose Source', 'Must make source available', 'OBLIGATION'),
    ('REPORT_USAGE', 'Report Usage', 'Must report usage statistics', 'OBLIGATION'),
    ('NOTIFY_LICENSOR', 'Notify Licensor', 'Must notify licensor of usage', 'OBLIGATION'),
    ('SAME_FORMAT', 'Maintain Format', 'Must preserve original format', 'OBLIGATION'),
    
    -- ============================================================================
    -- RESTRICTIONS: What you CANNOT do
    -- ============================================================================
    ('NO_COMMERCIAL', 'No Commercial Use', 'Commercial use not permitted', 'RESTRICTION'),
    ('NO_DERIVATIVES', 'No Derivatives', 'Cannot modify or create derivatives', 'RESTRICTION'),
    ('NO_SUBLICENSE', 'No Sublicensing', 'Cannot grant rights to others', 'RESTRICTION'),
    ('TERRITORY_LIMIT', 'Territory Restricted', 'Geographic limitations apply', 'RESTRICTION'),
    ('TIME_LIMIT', 'Time Limited', 'Rights expire after date', 'RESTRICTION'),
    ('NO_TRADEMARK', 'No Trademark Use', 'Cannot use trademarks', 'RESTRICTION'),
    ('NO_PATENT', 'No Patent Grant', 'No patent rights granted', 'RESTRICTION'),
    ('NO_WARRANTY', 'No Warranty', 'Provided as-is without warranty', 'RESTRICTION'),
    
    -- ============================================================================
    -- DBL-SPECIFIC PUBLICATION RIGHTS (from your XML example: see any licence.xml)
    -- ============================================================================
    ('allowIntroductions', 'Allow Introductions', 'May include book introductions', 'PERMISSION'),
    ('allowFootnotes', 'Allow Footnotes', 'May include footnotes', 'PERMISSION'),
    ('allowCrossReferences', 'Allow Cross-References', 'May include cross-references', 'PERMISSION'),
    ('allowExtendedNotes', 'Allow Extended Notes', 'May include extended study notes', 'PERMISSION');

-- ============================================================================
-- 2. LICENCES (Base templates)
-- ============================================================================

-- No License / All Rights Reserved
INSERT INTO audit.licences (code, name, version, link, summary, notes)
VALUES (
    'NONE',
    'No License',
    NULL,
    NULL,
    'All rights reserved - no permissions granted',
    'Default copyright - no usage permitted without explicit permission'
);

-- Public Domain
INSERT INTO audit.licences (code, name, version, link, summary, notes)
VALUES (
    'PUBLIC-DOMAIN',
    'Public Domain',
    NULL,
    NULL,
    'No copyright restrictions',
    'Work is in the public domain - free to use for any purpose'
);

INSERT INTO audit.licence_attribute_mapping (licence_id, attribute_code)
SELECT id, 'COMMERCIAL' FROM audit.licences WHERE code = 'PUBLIC-DOMAIN'
UNION ALL
SELECT id, 'DISTRIBUTE' FROM audit.licences WHERE code = 'PUBLIC-DOMAIN'
UNION ALL
SELECT id, 'MODIFY' FROM audit.licences WHERE code = 'PUBLIC-DOMAIN'
UNION ALL
SELECT id, 'TRANSLATE' FROM audit.licences WHERE code = 'PUBLIC-DOMAIN'
UNION ALL
SELECT id, 'PRINT' FROM audit.licences WHERE code = 'PUBLIC-DOMAIN'
UNION ALL
SELECT id, 'DIGITAL' FROM audit.licences WHERE code = 'PUBLIC-DOMAIN'
UNION ALL
SELECT id, 'AUDIO' FROM audit.licences WHERE code = 'PUBLIC-DOMAIN'
UNION ALL
SELECT id, 'VIDEO' FROM audit.licences WHERE code = 'PUBLIC-DOMAIN'
UNION ALL
SELECT id, 'SUBLICENSE' FROM audit.licences WHERE code = 'PUBLIC-DOMAIN'
UNION ALL
SELECT id, 'PRIVATE_USE' FROM audit.licences WHERE code = 'PUBLIC-DOMAIN';

-- CC0 1.0 Universal
INSERT INTO audit.licences (
    code, 
    name, 
    version, 
    link, 
    summary, 
    notes,
    source_id
)
VALUES (
    'CC0-1.0',
    'CC0 Universal',
    '1.0',
    'https://creativecommons.org/publicdomain/zero/1.0/',
    'Public domain dedication',
    'Creator waives all rights - equivalent to public domain',
    (SELECT id FROM audit.sources WHERE code = 'CC')
);

INSERT INTO audit.licence_attribute_mapping (licence_id, attribute_code)
SELECT id, 'COMMERCIAL' FROM audit.licences WHERE code = 'CC0-1.0'
UNION ALL
SELECT id, 'DISTRIBUTE' FROM audit.licences WHERE code = 'CC0-1.0'
UNION ALL
SELECT id, 'MODIFY' FROM audit.licences WHERE code = 'CC0-1.0'
UNION ALL
SELECT id, 'TRANSLATE' FROM audit.licences WHERE code = 'CC0-1.0'
UNION ALL
SELECT id, 'PRINT' FROM audit.licences WHERE code = 'CC0-1.0'
UNION ALL
SELECT id, 'DIGITAL' FROM audit.licences WHERE code = 'CC0-1.0'
UNION ALL
SELECT id, 'AUDIO' FROM audit.licences WHERE code = 'CC0-1.0'
UNION ALL
SELECT id, 'VIDEO' FROM audit.licences WHERE code = 'CC0-1.0'
UNION ALL
SELECT id, 'SUBLICENSE' FROM audit.licences WHERE code = 'CC0-1.0'
UNION ALL
SELECT id, 'PRIVATE_USE' FROM audit.licences WHERE code = 'CC0-1.0';

-- CC BY 4.0
INSERT INTO audit.licences (
    code, 
    name, 
    version, 
    link, 
    summary,
    source_id
)
VALUES (
    'CC-BY-4.0',
    'Attribution 4.0 International',
    '4.0',
    'https://creativecommons.org/licenses/by/4.0/',
    'Free to use with attribution',
    (SELECT id FROM audit.sources WHERE code = 'CC')
);

INSERT INTO audit.licence_attribute_mapping (licence_id, attribute_code)
SELECT id, 'COMMERCIAL' FROM audit.licences WHERE code = 'CC-BY-4.0'
UNION ALL
SELECT id, 'DISTRIBUTE' FROM audit.licences WHERE code = 'CC-BY-4.0'
UNION ALL
SELECT id, 'MODIFY' FROM audit.licences WHERE code = 'CC-BY-4.0'
UNION ALL
SELECT id, 'TRANSLATE' FROM audit.licences WHERE code = 'CC-BY-4.0'
UNION ALL
SELECT id, 'PRINT' FROM audit.licences WHERE code = 'CC-BY-4.0'
UNION ALL
SELECT id, 'DIGITAL' FROM audit.licences WHERE code = 'CC-BY-4.0'
UNION ALL
SELECT id, 'AUDIO' FROM audit.licences WHERE code = 'CC-BY-4.0'
UNION ALL
SELECT id, 'VIDEO' FROM audit.licences WHERE code = 'CC-BY-4.0'
UNION ALL
SELECT id, 'SUBLICENSE' FROM audit.licences WHERE code = 'CC-BY-4.0'
UNION ALL
SELECT id, 'PRIVATE_USE' FROM audit.licences WHERE code = 'CC-BY-4.0'
UNION ALL
SELECT id, 'ATTRIBUTION' FROM audit.licences WHERE code = 'CC-BY-4.0'
UNION ALL
SELECT id, 'NOTICE' FROM audit.licences WHERE code = 'CC-BY-4.0';

-- CC BY-SA 4.0
INSERT INTO audit.licences (
    code, 
    name, 
    version, 
    link, 
    summary,
    source_id
)
VALUES (
    'CC-BY-SA-4.0',
    'Attribution-ShareAlike 4.0 International',
    '4.0',
    'https://creativecommons.org/licenses/by-sa/4.0/',
    'Free to use with attribution, derivatives must use same license',
    (SELECT id FROM audit.sources WHERE code = 'CC')
);

INSERT INTO audit.licence_attribute_mapping (licence_id, attribute_code)
SELECT id, 'COMMERCIAL' FROM audit.licences WHERE code = 'CC-BY-SA-4.0'
UNION ALL
SELECT id, 'DISTRIBUTE' FROM audit.licences WHERE code = 'CC-BY-SA-4.0'
UNION ALL
SELECT id, 'MODIFY' FROM audit.licences WHERE code = 'CC-BY-SA-4.0'
UNION ALL
SELECT id, 'TRANSLATE' FROM audit.licences WHERE code = 'CC-BY-SA-4.0'
UNION ALL
SELECT id, 'PRINT' FROM audit.licences WHERE code = 'CC-BY-SA-4.0'
UNION ALL
SELECT id, 'DIGITAL' FROM audit.licences WHERE code = 'CC-BY-SA-4.0'
UNION ALL
SELECT id, 'AUDIO' FROM audit.licences WHERE code = 'CC-BY-SA-4.0'
UNION ALL
SELECT id, 'VIDEO' FROM audit.licences WHERE code = 'CC-BY-SA-4.0'
UNION ALL
SELECT id, 'SUBLICENSE' FROM audit.licences WHERE code = 'CC-BY-SA-4.0'
UNION ALL
SELECT id, 'PRIVATE_USE' FROM audit.licences WHERE code = 'CC-BY-SA-4.0'
UNION ALL
SELECT id, 'ATTRIBUTION' FROM audit.licences WHERE code = 'CC-BY-SA-4.0'
UNION ALL
SELECT id, 'NOTICE' FROM audit.licences WHERE code = 'CC-BY-SA-4.0'
UNION ALL
SELECT id, 'SHARE_ALIKE' FROM audit.licences WHERE code = 'CC-BY-SA-4.0';

-- CC BY-NC 4.0
INSERT INTO audit.licences (
    code, 
    name, 
    version, 
    link, 
    summary,
    source_id
)
VALUES (
    'CC-BY-NC-4.0',
    'Attribution-NonCommercial 4.0 International',
    '4.0',
    'https://creativecommons.org/licenses/by-nc/4.0/',
    'Free for non-commercial use with attribution',
    (SELECT id FROM audit.sources WHERE code = 'CC')
);

INSERT INTO audit.licence_attribute_mapping (licence_id, attribute_code)
SELECT id, 'DISTRIBUTE' FROM audit.licences WHERE code = 'CC-BY-NC-4.0'
UNION ALL
SELECT id, 'MODIFY' FROM audit.licences WHERE code = 'CC-BY-NC-4.0'
UNION ALL
SELECT id, 'TRANSLATE' FROM audit.licences WHERE code = 'CC-BY-NC-4.0'
UNION ALL
SELECT id, 'PRINT' FROM audit.licences WHERE code = 'CC-BY-NC-4.0'
UNION ALL
SELECT id, 'DIGITAL' FROM audit.licences WHERE code = 'CC-BY-NC-4.0'
UNION ALL
SELECT id, 'AUDIO' FROM audit.licences WHERE code = 'CC-BY-NC-4.0'
UNION ALL
SELECT id, 'VIDEO' FROM audit.licences WHERE code = 'CC-BY-NC-4.0'
UNION ALL
SELECT id, 'PRIVATE_USE' FROM audit.licences WHERE code = 'CC-BY-NC-4.0'
UNION ALL
SELECT id, 'ATTRIBUTION' FROM audit.licences WHERE code = 'CC-BY-NC-4.0'
UNION ALL
SELECT id, 'NOTICE' FROM audit.licences WHERE code = 'CC-BY-NC-4.0'
UNION ALL
SELECT id, 'NO_COMMERCIAL' FROM audit.licences WHERE code = 'CC-BY-NC-4.0';

-- CC BY-NC-SA 4.0
INSERT INTO audit.licences (
    code, 
    name, 
    version, 
    link, 
    summary,
    source_id
)
VALUES (
    'CC-BY-NC-SA-4.0',
    'Attribution-NonCommercial-ShareAlike 4.0 International',
    '4.0',
    'https://creativecommons.org/licenses/by-nc-sa/4.0/',
    'Free for non-commercial use with attribution, derivatives must use same license',
    (SELECT id FROM audit.sources WHERE code = 'CC')
);

INSERT INTO audit.licence_attribute_mapping (licence_id, attribute_code)
SELECT id, 'DISTRIBUTE' FROM audit.licences WHERE code = 'CC-BY-NC-SA-4.0'
UNION ALL
SELECT id, 'MODIFY' FROM audit.licences WHERE code = 'CC-BY-NC-SA-4.0'
UNION ALL
SELECT id, 'TRANSLATE' FROM audit.licences WHERE code = 'CC-BY-NC-SA-4.0'
UNION ALL
SELECT id, 'PRINT' FROM audit.licences WHERE code = 'CC-BY-NC-SA-4.0'
UNION ALL
SELECT id, 'DIGITAL' FROM audit.licences WHERE code = 'CC-BY-NC-SA-4.0'
UNION ALL
SELECT id, 'AUDIO' FROM audit.licences WHERE code = 'CC-BY-NC-SA-4.0'
UNION ALL
SELECT id, 'VIDEO' FROM audit.licences WHERE code = 'CC-BY-NC-SA-4.0'
UNION ALL
SELECT id, 'PRIVATE_USE' FROM audit.licences WHERE code = 'CC-BY-NC-SA-4.0'
UNION ALL
SELECT id, 'ATTRIBUTION' FROM audit.licences WHERE code = 'CC-BY-NC-SA-4.0'
UNION ALL
SELECT id, 'NOTICE' FROM audit.licences WHERE code = 'CC-BY-NC-SA-4.0'
UNION ALL
SELECT id, 'SHARE_ALIKE' FROM audit.licences WHERE code = 'CC-BY-NC-SA-4.0'
UNION ALL
SELECT id, 'NO_COMMERCIAL' FROM audit.licences WHERE code = 'CC-BY-NC-SA-4.0';

-- CC BY-ND 4.0
INSERT INTO audit.licences (
    code, 
    name, 
    version, 
    link, 
    summary,
    source_id
)
VALUES (
    'CC-BY-ND-4.0',
    'Attribution-NoDerivatives 4.0 International',
    '4.0',
    'https://creativecommons.org/licenses/by-nd/4.0/',
    'Free to use with attribution, no modifications allowed',
    (SELECT id FROM audit.sources WHERE code = 'CC')
);

INSERT INTO audit.licence_attribute_mapping (licence_id, attribute_code)
SELECT id, 'COMMERCIAL' FROM audit.licences WHERE code = 'CC-BY-ND-4.0'
UNION ALL
SELECT id, 'DISTRIBUTE' FROM audit.licences WHERE code = 'CC-BY-ND-4.0'
UNION ALL
SELECT id, 'PRINT' FROM audit.licences WHERE code = 'CC-BY-ND-4.0'
UNION ALL
SELECT id, 'DIGITAL' FROM audit.licences WHERE code = 'CC-BY-ND-4.0'
UNION ALL
SELECT id, 'PRIVATE_USE' FROM audit.licences WHERE code = 'CC-BY-ND-4.0'
UNION ALL
SELECT id, 'ATTRIBUTION' FROM audit.licences WHERE code = 'CC-BY-ND-4.0'
UNION ALL
SELECT id, 'NOTICE' FROM audit.licences WHERE code = 'CC-BY-ND-4.0'
UNION ALL
SELECT id, 'NO_DERIVATIVES' FROM audit.licences WHERE code = 'CC-BY-ND-4.0';

-- CC BY-NC-ND 4.0
INSERT INTO audit.licences (
    code, 
    name, 
    version, 
    link, 
    summary,
    source_id
)
VALUES (
    'CC-BY-NC-ND-4.0',
    'Attribution-NonCommercial-NoDerivatives 4.0 International',
    '4.0',
    'https://creativecommons.org/licenses/by-nc-nd/4.0/',
    'Free for non-commercial use with attribution, no modifications allowed',
    (SELECT id FROM audit.sources WHERE code = 'CC')
);

INSERT INTO audit.licence_attribute_mapping (licence_id, attribute_code)
SELECT id, 'DISTRIBUTE' FROM audit.licences WHERE code = 'CC-BY-NC-ND-4.0'
UNION ALL
SELECT id, 'PRINT' FROM audit.licences WHERE code = 'CC-BY-NC-ND-4.0'
UNION ALL
SELECT id, 'DIGITAL' FROM audit.licences WHERE code = 'CC-BY-NC-ND-4.0'
UNION ALL
SELECT id, 'PRIVATE_USE' FROM audit.licences WHERE code = 'CC-BY-NC-ND-4.0'
UNION ALL
SELECT id, 'ATTRIBUTION' FROM audit.licences WHERE code = 'CC-BY-NC-ND-4.0'
UNION ALL
SELECT id, 'NOTICE' FROM audit.licences WHERE code = 'CC-BY-NC-ND-4.0'
UNION ALL
SELECT id, 'NO_COMMERCIAL' FROM audit.licences WHERE code = 'CC-BY-NC-ND-4.0'
UNION ALL
SELECT id, 'NO_DERIVATIVES' FROM audit.licences WHERE code = 'CC-BY-NC-ND-4.0';

-- ============================================================================
-- 3. EXAMPLE: DBL AGREEMENT
-- ============================================================================

-- Example: WEB Bible Public Domain agreement with DBL publication rights
-- INSERT INTO audit.dbl_agreements (
--     agreement_id,
--     dbl_id,
--     licence_file_id,
--     base_licence_id,
--     notes
-- )
-- VALUES (
--     1,
--     'ENGWEB',
--     123,  -- Your file ID
--     (SELECT id FROM audit.licences WHERE code = 'PUBLIC-DOMAIN'),
--     'WEB Bible - Public Domain with DBL-specific publication rights'
-- );

-- -- Add DBL publication rights
-- INSERT INTO audit.agreement_attributes (agreement_id, attribute_code, attribute_value)
-- VALUES 
--     (1, 'allowIntroductions', 'true'),
--     (1, 'allowFootnotes', 'true'),
--     (1, 'allowCrossReferences', 'true'),
--     (1, 'allowExtendedNotes', 'false');