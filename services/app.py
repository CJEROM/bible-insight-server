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

def initialise_database():
    base = Path(__file__).parent
    scripts_dir = base / "scripts"

    print("Waiting for containers ...")
    time.sleep(5)

    subprocess.run(
        ["python3", "init_database.py"], 
        cwd=scripts_dir
    )


def start_api_server():
    base = Path(__file__).parent
    scripts_dir = base / "api"

    subprocess.Popen(
        ["python3", "api.py"], 
        cwd=scripts_dir
    )

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
        initialise_database()
        # start_api_server() 
        print("FINISHED Script")
    except:
        pass
    