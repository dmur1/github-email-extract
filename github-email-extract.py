import sys
import requests
import subprocess
import tempfile
import os

def get_user_repository_https_urls(username):
    url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(url)

    if response.status_code == 200:
        repositories = response.json()
        https_urls = [repo['html_url'] + '.git' for repo in repositories]
        return https_urls
    else:
        print(f"Error: {response.status_code}")
        return None

def create_temp_directory():
    temp_dir = tempfile.mkdtemp()
    return temp_dir

def clone_and_run_command(https_url, destination_path='.'):
    temp_dir = create_temp_directory()
    try:
        subprocess.run(['git', 'clone', https_url, temp_dir], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        command = 'git log | grep "Author:" | sort | uniq'
        subprocess.run(command, shell=True, cwd=temp_dir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository or running command: {e}")
    finally:
        cleanup_temp_directory(temp_dir)

def cleanup_temp_directory(temp_dir):
    if os.path.exists(temp_dir):
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                os.rmdir(dir_path)
        os.rmdir(temp_dir)

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <github_username>")
        sys.exit(1)

    username = sys.argv[1]
    https_urls = get_user_repository_https_urls(username)

    if https_urls:
        for https_url in https_urls:
            clone_and_run_command(https_url)

if __name__ == "__main__":
    main()
