import os
import shlex
import subprocess
import sys
from typing import List

from dotenv import load_dotenv

load_dotenv()
GCP_COMPOSER_BUCKET_ENV_VAR = "GCP_COMPOSER_BUCKET"


def deploy(files:List[str]) -> None:
    if len(files) > 0:
        bucket = os.environ.get(GCP_COMPOSER_BUCKET_ENV_VAR)
        subprocess.run(shlex.split(f"cat .changeset.deploy | gsutil -m cp -I {bucket}"))
        file_output = "".join([f" * {file}\n" for file in files])
        print(f"Succesfully loaded: \n{file_output}")
    else:
        print('No airflow changes to deploy')

if __name__ == "__main__":
    files = [file.strip() for file in sys.stdin.readlines()]
    deploy(files)