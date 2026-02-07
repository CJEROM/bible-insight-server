Rule: All database access must go through database/queries.

Consider Lint rules (they help enforce good practice by defining where you can code particular things)

Forbidden:

- raw SQL in ingestors
- SQLAlchemy select() outside database/
