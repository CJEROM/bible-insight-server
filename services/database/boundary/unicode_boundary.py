from database.boundary.base_boundary import ReadBoundary, WriteBoundary, DeleteBoundary

class UnicodeReadBoundary(ReadBoundary):
    pass

class UnicodeWriteBoundary(WriteBoundary):
    def persist_script(self,
            code            : str,
            numeric         : int,
            name            : str,
            unicode_age     : str,
            date_added      : str
        ) -> None:

        query = """
            INSERT INTO standards.iso15924_scripts (code, numeric, name, unicode_age, date_added)
            VALUES (%s, %s, %s, %s, %s)
        """
        self.db.execute(query, (code, numeric, name, unicode_age, date_added))

class UnicodeDeleteBoundary(DeleteBoundary):
    pass