from database.boundary.base_boundary import ReadBoundary, WriteBoundary, DeleteBoundary

class StepBibleReadBoundary(ReadBoundary):
    def find_morph_code(self, 
            code: str    
        ):
        query = """
            SELECT code FROM morphology.codes WHERE code = %s
        """
        found_code = self.db.fetch_clean_one(query, (code,))
        return found_code

class StepBibleWriteBoundary(WriteBoundary):
    # ============================================================================
    #                                   TAGGED BIBLE
    # ============================================================================

    def write_tagnt(self, 
        verse                   : str,
        word_position           : str,
        word_type               : str,
        greek                   : str,
        transliteration         : str,
        english                 : str,
        dStrong                 : str,
        grammar                 : str,
        dictionary_form         : str,
        gloss                   : str,
        editions                : str,
        meaning_variants        : str,
        spelling_variants       : str,
        spanish                 : str,
        sub_meanings            : str,
        conjoined_data          : str,
        sStrong                 : str,
        instance                : str,
        alt_strongs             : str,
        variant_notes           : str
    ):
        query = """
            INSERT INTO stepbible.tagnt (
                verse, word_position, word_type, greek, transliteration, english, d_strong, grammar, dictionary_form, gloss, editions, meaning_variants, spelling_variants, spanish, sub_meanings, conjoined_data, s_strong, instance, alt_strongs, variant_notes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        self.db.execute(query, (
            verse, word_position, word_type, greek, transliteration, english, dStrong, grammar, dictionary_form, gloss, editions, meaning_variants, spelling_variants, spanish, sub_meanings, conjoined_data, sStrong, instance, alt_strongs, variant_notes
        ))

    # ============================================================================
    #                                   MORPHOLOGY
    # ============================================================================

    def write_morphological_code(self, 
            iso         : str,
            code        : str,
            morphology  : str,
            explanation : str,
            example     : str,
            source_id   : int,
            raw_data    : str
        ):
        query = """
            INSERT INTO morphology.codes (
                iso, code, morphology, explanation, example, source_id, raw_data
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        code_id = self.db.fetch_clean_one(query, (
            iso, code, morphology, explanation, example, source_id, raw_data
        ))
        return code_id 
    
    def write_morphology_features(self,
            name        : str,
            description : str = None
        ) -> int: 
        query = """
            INSERT INTO morphology.features (name, description)
            VALUES (%s, %s)
            ON CONFLICT (name)
            DO UPDATE SET description = morphology.features.description
            RETURNING id;
        """
        feature_id = self.db.fetch_clean_one(query, (
            name, description
        ))
        return feature_id 
    
    def write_morphology_feature_value(self,
            feature_id  : int,
            feature     : str,
            value       : str,
            description : str = None
        ) -> int: 
        query = """
            INSERT INTO morphology.feature_values (
                feature_id, feature, value, description
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (feature_id, value)
            DO UPDATE SET description = morphology.feature_values.description
            RETURNING id;
        """
        feature_id = self.db.fetch_clean_one(query, (
            feature_id, feature, value, description
        ))
        return feature_id 
    
    def write_morphology_derived_feature_value(self,
            from_value      : int,
            derived_value   : int
        ) -> None: 
        query = """
            INSERT INTO morphology.derived_feature_values (
                from_value_id, derived_value
            ) VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """
        self.db.execute(query, (
            from_value, derived_value
        ))

    def write_morphology_code_values(self,
            code_id     : int,
            value_id    : int
        ) -> None: 
        query = """
            INSERT INTO morphology.code_values (
                code_id, value_id
            ) VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """
        self.db.execute(query, (
            code_id, value_id
        ))
    
    # ============================================================================
    #                                   LEXICON
    # ============================================================================

    def map_lexicon_morph_codes(self,
            data_id         : int,
            position        : str,
            relation_type   : str,
            language        : str,
            sub_code        : str
        ) -> None: 
        query = """
            INSERT INTO lexicon.morph_mapping (
                data_id, position, relation_type, language, sub_code
            ) VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """
        self.db.execute(query, (
            data_id, position, relation_type, language, sub_code
        ))

    def write_lexicon_data(self,
            e_strong            : str,
            d_strong            : str,
            d_u_relationship    : str,
            u_strong            : str,
            text                : str,
            transliteration     : str,
            morph               : str,
            gloss               : str,
            meaning             : str,
            source_id           : int,
        ) -> int: 
        query = """
            INSERT INTO lexicon.data (
                e_strong, d_strong, d_u_relationship, u_strong, text, transliteration, morph, gloss, meaning, source_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        data_id = self.db.fetch_clean_one(query, (
            e_strong, d_strong, d_u_relationship, u_strong, text, transliteration, morph, gloss, meaning, source_id
        ))
        return data_id

class StepBibleDeleteBoundary(DeleteBoundary):
    pass