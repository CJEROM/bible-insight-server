from database.boundary.base_boundary import ReadBoundary, WriteBoundary, DeleteBoundary

class SILReadBoundary(ReadBoundary):
    # figure out whether iso code is present in the database
    def is_iso_code(self,
            iso_code    : str            
        ):
        query = """
            SELECT * FROM sil.iso_codes WHERE id = %s;
        """
        result = self.db.fetch_one(query, (iso_code, ))
        return True if result else False
    
    def get_retirement(self,
            iso_code    : str            
        ):
        query = """
            SELECT id FROM sil.retirements WHERE iso_code = %s;
        """
        retirement_id = self.db.fetch_one(query, (iso_code, ))
        return retirement_id

class SILWriteBoundary(WriteBoundary):
    def persist_iso_code(self,
            iso_code        : str,
            part2b          : str,
            part2t          : str,
            part1           : str,
            scope           : str,
            type            : str,
            ref_name        : str,
            status          : str,
            comment         : str
        ) -> None:
        query = """
            INSERT INTO sil.iso_codes (id, part2b, part2t, part1, scope, type, ref_name, comment, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.db.execute(query, (iso_code, part2b, part2t, part1, scope, type, ref_name, comment, status))

    def persist_iso_names(self,
            iso_code        : str,
            print_name      : str,
            inverted_name   : str
        ) -> None:

        query = """
            INSERT INTO sil.iso_names (iso_code, print_name, inverted_name)
            VALUES (%s, %s, %s)
        """
        self.db.execute(query, (iso_code, print_name, inverted_name))

    def persist_iso_macrolanguage(self,
            macro_id    : str,
            iso_id      : str,
            iso_status  : str
        ) -> None:
        query = """
            INSERT INTO sil.macrolanguages (macro_id, iso_id, iso_status)
            VALUES (%s, %s, %s)
        """
        self.db.execute(query, (macro_id, iso_id, iso_status))

    def persist_iso_retirements(self,
            iso_code        : str,
            ref_name        : str,
            retired_reason  : str,
            retired_remedy  : str,
            effective       : str
        ) -> int:
        query = """
            INSERT INTO sil.retirements (iso_code, ref_name, retired_reason, retired_remedy, effective)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """
        retirement_id = self.db.fetch_clean_one(query, (iso_code, ref_name, retired_reason, retired_remedy, effective))
        return retirement_id

    def persist_iso_retirement_changes(self,
            retirement_id   : int,
            changed_to      : str
        ) -> None:
        query = """
            INSERT INTO sil.retirement_changes (retirement_id, changed_to)
            VALUES (%s, %s)
        """
        self.db.execute(query, (retirement_id, changed_to))

class SILDeleteBoundary(DeleteBoundary):
    pass