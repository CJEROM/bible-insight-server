from database.boundary.base_boundary import ReadBoundary, WriteBoundary, DeleteBoundary

class StepBibleReadBoundary(ReadBoundary):
    pass    

class StepBibleWriteBoundary(WriteBoundary):
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

class StepBibleDeleteBoundary(DeleteBoundary):
    pass