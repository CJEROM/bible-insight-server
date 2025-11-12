import subprocess
import os
from datetime import datetime
import argparse

from dotenv import load_dotenv
from pathlib import Path

USE_ENV = True

if USE_ENV:
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
else:
    POSTGRES_USERNAME = "postgres"
    POSTGRES_PASSWORD = "postgres"
    POSTGRES_DB = "postgres"
    POSTGRES_HOST = "localhost"
    POSTGRES_PORT = "5432"



BACKUP_DIR = Path(__file__).parents[2] / "backups" # Creates it in root repo folder
os.makedirs(BACKUP_DIR, exist_ok=True)

def choose_backup_file():
    backups = sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.endswith(".sql")],
        reverse=True
    )
    if not backups:
        print("❌ No backup files found in backup directory.")
        return None

    print("\nAvailable backups:")
    for i, b in enumerate(backups, start=1):
        print(f"  [{i}] {b}")

    # Ask user to choose
    while True:
        try:
            choice = int(input("\nEnter number of the backup to restore: "))
            if 1 <= choice <= len(backups):
                return os.path.join(BACKUP_DIR, backups[choice - 1])
            else:
                print("Invalid selection, try again.")
        except ValueError:
            print("Please enter a valid number.")

def backup_database():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"{POSTGRES_DB}_{timestamp}.sql")

    # Use environment variable for password security
    env = os.environ.copy()
    env["PGPASSWORD"] = POSTGRES_PASSWORD

    command = [
        "pg_dump",
        "-h", POSTGRES_HOST,
        "-p", POSTGRES_PORT,
        "-U", POSTGRES_USERNAME,
        "-F", "p",  # plain SQL
        "-d", POSTGRES_DB,
        "-f", backup_file
    ]

    print(f"Backing up database '{POSTGRES_DB}' to {backup_file}...")
    subprocess.run(command, env=env, check=True)
    print("✅ Backup completed successfully.")
    return backup_file


def restore_database(backup_file):
    env = os.environ.copy()
    env["PGPASSWORD"] = POSTGRES_PASSWORD

    # If no backup file provided, show selection menu
    if not backup_file:
        backup_file = choose_backup_file()
        if not backup_file:
            return

    print(f"\nRestoring database '{POSTGRES_DB}' from {backup_file}...")

    # Drop and recreate the database
    drop_command = [
        "psql", "-h", POSTGRES_HOST, "-p", POSTGRES_PORT, "-U", POSTGRES_USERNAME,
        "-d", "template1",
        "-c", f"DROP DATABASE IF EXISTS {POSTGRES_DB};"
    ]
    create_command = [
        "psql", "-h", POSTGRES_HOST, "-p", POSTGRES_PORT, "-U", POSTGRES_USERNAME,
        "-d", "template1",
        "-c", f"CREATE DATABASE {POSTGRES_DB};"
    ]
    restore_command = [
        "psql", "-h", POSTGRES_HOST, "-p", POSTGRES_PORT, "-U", POSTGRES_USERNAME,
        "-d", POSTGRES_DB, "-f", backup_file
    ]
    # restore_command = [
    #     "pg_restore",
    #     "-h", POSTGRES_HOST,
    #     "-p", POSTGRES_PORT,
    #     "-U", POSTGRES_USERNAME,
    #     "-d", POSTGRES_DB,
    #     "--clean", "--if-exists",
    #     backup_file  # 👈 just the file name, no -f
    # ]

    subprocess.run(drop_command, env=env, check=True)
    subprocess.run(create_command, env=env, check=True)
    subprocess.run(restore_command, env=env, check=True)

    print("✅ Restore completed successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PostgreSQL Backup & Restore Utility")
    parser.add_argument("--backup", action="store_true", help="Perform a database backup")
    parser.add_argument("--restore", nargs="?", const=None, help="Restore database (optionally specify a file)")

    args = parser.parse_args()

    if args.backup:
        backup_database()
    elif args.restore is not None:
        restore_database(args.restore)
    elif args.restore is None:
        restore_database(None)
    else:
        parser.print_help()
