INSERT INTO audit.license_providers (provider_code, name, description) 
VALUES 
	('CC', 'Creative Commons', 'Content licenses'),
	('GNU', 'GNU / FSF (Free Software Foundation)', 'Free Software licenses'),
	('CUST', 'Custom Agreement / License', 'DBL / SIL / Negotiated'),
	('NONE', 'No License', 'No License');

INSERT INTO audit.license_attributes (provider_code, attribute_code, name, description, attribute_type) 
VALUES 
	('CC', 'BY', 'Attribution', 'Credit must be given to the creator', 'obligation'),
	('CC', 'SA', 'Share Alike', 'Adaptations must be shared under the same terms', 'obligation'),
	('CC', 'NC', 'Non Commercial', 'Only noncommercial uses of the work are permitted', 'restriction'),
	('CC', 'ND', 'No Derivatives', 'No derivatives or adaptations of the work are permitted', 'restriction'),
	('CC', '0', 'No Rights Reserved', 'Public Domain - No copyright restrictions', 'permission');
	-- ('GNU', '', '', '', '');

INSERT INTO audit.licenses (provider_code, code, name, version, link) 
VALUES 
	('NONE', 'NONE', 'No License', '0', NULL),
	('CC', 'BY-NC-ND', 'Attribution-Non', '4.0', 'https://creativecommons.org/licenses/by-nc-nd/4.0/'),
	('CC', 'BY-ND', 'Attribution-NoDerivatives 4.0 International', '4.0', 'https://creativecommons.org/licenses/by-nd/4.0/'),
	('CC', 'BY-NC-SA', 'Attribution-NonCommercial-ShareAlike 4.0 International', '4.0', 'https://creativecommons.org/licenses/by-nc-sa/4.0/'),
	('CC', 'BY-NC', 'Attribution-NonCommercial 4.0 International', '4.0', 'https://creativecommons.org/licenses/by-nc/4.0/'),
	('CC', 'BY-SA', 'Attribution-ShareAlike 4.0 International', '4.0', 'https://creativecommons.org/licenses/by-sa/4.0/'),
	('CC', 'BY', 'Attribution 4.0 International', '4.0', 'https://creativecommons.org/licenses/by/4.0/'),
	('CC', '0', '', '1.0', 'https://creativecommons.org/publicdomain/zero/');
	-- ('GNU', 'GPLv3', '', '', ''),
	-- ('GNU', 'GPLv2', '', '', ''),
	-- ('', '', '', '', ''),
	-- ('', '', '', '', ''),;

INSERT INTO audit.license_attribute_mapping (license_id, agreement_id, provider_code, attribute_code) 
VALUES 
	(2, NULL, 'CC', 'BY'),
	(2, NULL, 'CC', 'NC'),
	(2, NULL, 'CC', 'ND'),
	(3, NULL, 'CC', 'BY'),
	(3, NULL, 'CC', 'ND'),
	(4, NULL, 'CC', 'BY'),
	(4, NULL, 'CC', 'NC'),
	(4, NULL, 'CC', 'SA'),
	(5, NULL, 'CC', 'BY'),
	(5, NULL, 'CC', 'NC'),
	(6, NULL, 'CC', 'BY'),
	(6, NULL, 'CC', 'SA'),
	(7, NULL, 'CC', 'BY'),
	(8, NULL, 'CC', '0');
	-- (9, NULL, 'GNU', ''),
	-- (10, NULL, 'GNU', ''),;