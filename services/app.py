from pathlib import Path
import subprocess
import requests
import time
import os
import shutil

def restart_docker(container):
    base = Path(__file__).parent.parent
    scripts_dir = base / "devops/docker" / container

    # Destroy existing instance + connected volumes
    subprocess.run(
        ["docker", "compose", "down", "-v"], 
        cwd=scripts_dir,
        check=True # Allows it to catch errors
    )

    # Delete any folders inside this containers folder
    for root, dirs, files in os.walk(scripts_dir, topdown=False):
        for d in dirs:
            dir_path = os.path.join(root, d)
            print(f"Deleting folder: {dir_path}")
            shutil.rmtree(dir_path)  # removes the entire directory and its contents

    # Restart Docker instance
    subprocess.run(["docker", "compose", "up", "-d"], cwd=scripts_dir)

def initialise_script(file_name, delay):
    base = Path(__file__).parent
    scripts_dir = base / "scripts"

    time.sleep(delay)

    subprocess.run(
        ["python3", file_name], 
        cwd=scripts_dir
    )

def run_script(file_name):
    base = Path(__file__).parent
    scripts_dir = base

    subprocess.run(
        ["python3", file_name], 
        cwd=scripts_dir
    )

def create_database_backup():
    base = Path(__file__).parent
    scripts_dir = base / "scripts"

    subprocess.Popen(
        ["python3", "pg_backup_restore.py", "--backup"], 
        cwd=scripts_dir
    )

def start_api_server():
    base = Path(__file__).parent
    scripts_dir = base / "api"

    subprocess.Popen(
        ["python3", "api.py"], 
        cwd=scripts_dir
    )

    time.sleep(1)

    base_url = "http://REDACTED_IP:5000/"
    response = requests.get(base_url+"init_database")
    print(response.status_code, response.text)

if __name__ == "__main__":
    # Check database instance working properly (issue with image on mac)
    try:
        restart_docker("postgres")
    except Exception as e:
        restart_docker("postgres-mac")

    try:
        # restart_docker("minio")
        # restart_docker("label-studio")
        # restart_docker("authentik")
        # restart_docker("memgraph")
        initialise_script("init_database.py", 5)
        # initialise_script("init_minio.py", 0)
        # initialise_script("init_labelstudio.py", 60) # Label Studio has a long delay before operational
        # # start_api_server() 
        # run_script(".\ingestor\ingestor.py")
        # create_database_backup()
        # run_script(".\labeller\labeller.py")
        # print("FINISHED Script")
    except Exception as e:
        pass
    