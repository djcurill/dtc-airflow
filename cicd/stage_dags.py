import os
import sys
from dotenv import load_dotenv
import shlex
import subprocess

load_dotenv()
GCP_COMPOSER_BUCKET_ENV_VAR = "GCP_COMPOSER_BUCKET"

def deploy() -> None:
    changed_files = [file.strip() for file in sys.stdin.readlines()]
    if len(changed_files) > 0:
        bucket = os.environ.get(GCP_COMPOSER_BUCKET_ENV_VAR)
        subprocess.run(shlex.split(f"cat .changeset.python | gsutil -m cp -I {bucket}"))
        file_output = "".join([f" * {file}\n" for file in changed_files])
        print(f"Succesfully loaded: \n{file_output}")
    else:
        print('No airflow changes to deploy')

if __name__ == "__main__":
    deploy()