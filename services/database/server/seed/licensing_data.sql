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
    ('NO_DISTRIBUTION', 'No Distribution', 'Do not provide a means to redistribute', 'RESTRICTION'),
    ('NO_ENDORSEMENT', 'No Endorsement', 'Use of the material must not imply endorsement or approval by the original author or organization.', 'RESTRICTION'),

    -- ============================================================================
    -- DBL-SPECIFIC PUBLICATION RIGHTS (from your XML example: see any licence.xml)
    -- ============================================================================
    ('allowIntroductions', 'Allow Introductions', 'May include book introductions', 'PERMISSION'),
    ('allowFootnotes', 'Allow Footnotes', 'May include footnotes', 'PERMISSION'),
    ('allowCrossReferences', 'Allow Cross-References', 'May include cross-references', 'PERMISSION'),
    ('allowExtendedNotes', 'Allow Extended Notes', 'May include extended study notes', 'PERMISSION');

-- ============================================================================
-- GPL/COPYLEFT-SPECIFIC ATTRIBUTES
-- ============================================================================

INSERT INTO audit.licence_attributes (attribute_code, name, description, attribute_type)
VALUES 
    -- PERMISSIONS
    ('USE', 'Use', 'May use the software', 'PERMISSION'),
    ('STUDY', 'Study', 'May study how the program works', 'PERMISSION'),
    ('PATENT_GRANT', 'Patent Grant', 'Contributors grant patent rights', 'PERMISSION'),
    
    -- OBLIGATIONS
    ('COPYLEFT', 'Copyleft', 'Derivative works must use same or compatible license', 'OBLIGATION'),
    ('SOURCE_CODE', 'Source Code Disclosure', 'Must provide source code or make it available', 'OBLIGATION'),
    ('INSTALLATION_INFO', 'Installation Information', 'Must provide installation instructions (GPLv3)', 'OBLIGATION'),
    ('PRESERVE_NOTICES', 'Preserve Notices', 'Must keep copyright and license notices intact', 'OBLIGATION'),
    ('DOCUMENT_CHANGES', 'Document Changes', 'Must state changes made to the work', 'OBLIGATION'),
    ('LICENSE_TEXT', 'Include License Text', 'Must include full text of license', 'OBLIGATION'),
    ('NETWORK_DISCLOSURE', 'Network Use Disclosure', 'Must provide source for network use (AGPL)', 'OBLIGATION'),
    
    -- RESTRICTIONS
    ('NO_DRM', 'No DRM', 'Cannot add effective technological protection measures', 'RESTRICTION'),
    ('NO_ADDITIONAL_RESTRICTIONS', 'No Additional Restrictions', 'Cannot impose further restrictions on recipients', 'RESTRICTION'),
    ('NO_TIVOIZATION', 'No Tivoization', 'Cannot prevent users from running modified versions (GPLv3)', 'RESTRICTION');

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
--     (SELECT id FROM audit.licences WHERE code = 'PUBLIC_DOMAIN'),
--     'WEB Bible - Public Domain with DBL-specific publication rights'
-- );

-- -- Add DBL publication rights
-- INSERT INTO audit.agreement_attributes (agreement_id, attribute_code, attribute_value)
-- VALUES 
--     (1, 'allowIntroductions', 'true'),
--     (1, 'allowFootnotes', 'true'),
--     (1, 'allowCrossReferences', 'true'),
--     (1, 'allowExtendedNotes', 'false');