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
            source_id   : int,
            raw_data    : str
        ):
        query = """
            INSERT INTO morphology.lexical_codes (
                iso, code, morphology, explanation, source_id, raw_data
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        code_id = self.db.fetch_clean_one(query, (
            iso, code, morphology, explanation, source_id, raw_data
        ))
        return code_id 
    
class StepBibleDeleteBoundary(DeleteBoundary):
    pass