import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

# Automatically find the project root (folder containing .env)
current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / ".env").exists():
        load_dotenv(parent / ".env")
        break

POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

def init_database():
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USERNAME,
        password=POSTGRES_PASSWORD
    )

    cur = conn.cursor()

    # cur.execute("SELECT version();")
    cur.execute("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_name = %s
        );
    """, ("languages",))
    
    if cur.fetchone()[0] == True:
        return "Database Already Initialised!"

    # Load and execute SQL file
    with open("../database/server/schemas/v1_schema.sql", "r") as file:
        sql_script = file.read()
        cur.execute(sql_script)

    migrations = [
        "001_init_translations.sql",
        "002_init_bible.sql"
    ]

    for init_script in migrations:
        script_path = "../database/server/migrations/" + init_script
        # Load and execute SQL file
        with open(script_path, "r", encoding="utf-8") as file:
            sql_script = file.read()
            cur.execute(sql_script)

    conn.commit()
    cur.close()
    conn.close()

    print("Database Init Success")

if __name__ == "__main__":
    init_database()