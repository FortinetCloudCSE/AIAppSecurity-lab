import os
import shlex
import subprocess
from pathlib import Path

import boto3

ALLOWED_COMMANDS = {"echo", "pwd", "ls", "whoami", "uname", "date"}


def read_resume_text(location: str) -> str:
    if not location:
        return "No resume location was provided."

    if location.startswith("s3://"):
        bucket_key = location.replace("s3://", "", 1)
        bucket, key = bucket_key.split("/", 1)
        s3 = boto3.client("s3")
        response = s3.get_object(Bucket=bucket, Key=key)
        body = response["Body"].read().decode("utf-8", errors="ignore")
        return body[:12000]

    path = Path(location)
    if not path.exists():
        return f"Resume not found at {location}"

    return path.read_text(encoding="utf-8", errors="ignore")[:12000]



def run_command(command: str) -> dict:
    if not command.strip():
        return {"blocked": True, "stdout": "", "stderr": "Empty command", "returncode": 1}

    parts = shlex.split(command)
    base = parts[0]

    if base not in ALLOWED_COMMANDS:
        return {
            "blocked": True,
            "stdout": "",
            "stderr": f"Command '{base}' is not allowed in this demo.",
            "returncode": 1,
        }

    completed = subprocess.run(
        parts,
        capture_output=True,
        text=True,
        timeout=10,
        cwd=os.getcwd(),
    )
    return {
        "blocked": False,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "returncode": completed.returncode,
    }
