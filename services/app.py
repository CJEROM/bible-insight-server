from pathlib import Path
import subprocess
import requests
import time

def restart_docker(container):
    base = Path(__file__).parent.parent
    scripts_dir = base / "devops/docker" / container

    # Destroy existing instance + connected volumes
    subprocess.run(["docker", "compose", "down", "-v"], cwd=scripts_dir)
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
    try:
        restart_docker("postgres")
        restart_docker("minio")
        # restart_docker("authentik")
        # restart_docker("memgraph")
        # restart_docker("label-studio")
        initialise_script("init_database.py", 3)
        initialise_script("init_minio.py", 0)
        # start_api_server() 
        print("FINISHED Script")
    except:
        pass
    