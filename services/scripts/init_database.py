import psycopg2

def init_database():
    conn = psycopg2.connect(
        host="REDACTED_IP",
        port=5444,
        dbname="postgres",
        user="postgres",
        password="REDACTED_PASSWORD"
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
        with open(script_path, "r") as file:
            sql_script = file.read()
            cur.execute(sql_script)

    conn.commit()
    cur.close()
    conn.close()

    print("Database Init Success")

if __name__ == "__main__":
    init_database()