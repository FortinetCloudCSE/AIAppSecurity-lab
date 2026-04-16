import logging
import os
import shlex
import subprocess
import tempfile
from pathlib import Path
from typing import Union

import boto3

DISALLOWED_COMMANDS = {"sh"}
ALLOWED_AWS_ACTION_PREFIXES = ("get", "list", "describe")
UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
TMP_RESUME_DIR = Path(tempfile.gettempdir()) / "aiapp-resumes"
logger = logging.getLogger(__name__)


def upload_resume_file(path: Union[str, Path], filename: str) -> str:
    bucket_name = os.getenv("S3_BUCKET_NAME", "").strip()
    if not bucket_name:
        logger.info("upload_resume_file local_only path=%s", path)
        return str(path)

    key = f"resumes/{filename}"
    region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
    s3 = boto3.client("s3", region_name=region)
    logger.info("upload_resume_file s3_upload bucket=%s key=%s source=%s", bucket_name, key, path)
    s3.upload_file(str(path), bucket_name, key)
    return f"s3://{bucket_name}/{key}"


def list_synced_resume_files() -> list[str]:
    if not TMP_RESUME_DIR.exists():
        return []

    return sorted(
        str(path)
        for path in TMP_RESUME_DIR.iterdir()
        if path.is_file() and path.name != ".gitkeep"
    )


def sync_resumes_from_bucket() -> list[str]:
    bucket_name = os.getenv("S3_BUCKET_NAME", "").strip()
    if not bucket_name:
        logger.info("sync_resumes_from_bucket skipped reason=no_bucket_configured")
        return []

    region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
    s3 = boto3.client("s3", region_name=region)
    logger.info("sync_resumes_from_bucket start bucket=%s region=%s target_dir=%s", bucket_name, region, TMP_RESUME_DIR)
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix="resumes/")

    TMP_RESUME_DIR.mkdir(parents=True, exist_ok=True)
    for existing_file in TMP_RESUME_DIR.iterdir():
        if existing_file.is_file():
            logger.info("sync_resumes_from_bucket remove_stale_file path=%s", existing_file)
            existing_file.unlink()

    downloaded_files: list[str] = []
    for item in response.get("Contents", []):
        key = item.get("Key", "")
        if not key or key.endswith("/"):
            continue

        local_name = Path(key).name
        local_path = TMP_RESUME_DIR / local_name
        logger.info("sync_resumes_from_bucket download bucket=%s key=%s local_path=%s", bucket_name, key, local_path)
        s3.download_file(bucket_name, key, str(local_path))
        downloaded_files.append(str(local_path))

    logger.info("sync_resumes_from_bucket complete downloaded_count=%s files=%s", len(downloaded_files), downloaded_files)
    return sorted(downloaded_files)


def get_all_resume_contents() -> list[dict[str, str]]:
    resume_files = sync_resumes_from_bucket()
    resume_contents: list[dict[str, str]] = []
    for resume_file in resume_files:
        content = read_resume_text(resume_file)
        logger.info(
            "get_all_resume_contents resume=%s content_preview=%r",
            resume_file,
            content[:500],
        )
        resume_contents.append(
            {
                "location": resume_file,
                "content": content,
            }
        )
    logger.info("get_all_resume_contents complete resume_count=%s", len(resume_contents))
    return resume_contents


def read_resume_text(location: str) -> str:
    if not location:
        return "No resume location was provided."

    if location.startswith("s3://"):
        bucket_key = location.replace("s3://", "", 1)
        bucket, key = bucket_key.split("/", 1)
        s3 = boto3.client("s3")
        logger.info("read_resume_text s3_read bucket=%s key=%s", bucket, key)
        response = s3.get_object(Bucket=bucket, Key=key)
        body = response["Body"].read().decode("utf-8", errors="ignore")
        return body[:12000]

    path = Path(location)
    if not path.exists():
        logger.warning("read_resume_text missing path=%s", location)
        return f"Resume not found at {location}"

    content = path.read_text(encoding="utf-8", errors="ignore")[:12000]
    logger.info("read_resume_text local_read path=%s content_preview=%r", location, content[:500])
    return content



def run_command(command: str) -> dict:
    if not command.strip():
        return {"blocked": True, "stdout": "", "stderr": "Empty command", "returncode": 1}

    parts = shlex.split(command)
    base = parts[0]

    logger.info("run_command start command=%r base=%s", command, base)

    if base in DISALLOWED_COMMANDS:
        logger.warning("run_command blocked command=%r reason=disallowed_base", command)
        return {
            "blocked": True,
            "stdout": "",
            "stderr": f"Command '{base}' is not allowed in this demo.",
            "returncode": 1,
        }

    try:
        completed = subprocess.run(
            parts,
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.getcwd(),
        )
    except FileNotFoundError:
        logger.exception("run_command missing_binary command=%r base=%s", command, base)
        return {
            "blocked": False,
            "stdout": "",
            "stderr": f"Command '{base}' is not installed in the container.",
            "returncode": 127,
        }
    except subprocess.TimeoutExpired:
        logger.exception("run_command timeout command=%r", command)
        return {
            "blocked": False,
            "stdout": "",
            "stderr": f"Command timed out after 10 seconds: {command}",
            "returncode": 124,
        }

    logger.info(
        "run_command complete command=%r returncode=%s stdout=%r stderr=%r",
        command,
        completed.returncode,
        completed.stdout[:500],
        completed.stderr[:500],
    )
    return {
        "blocked": False,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "returncode": completed.returncode,
    }


def fetch_aws_account_info(command: str) -> dict:
    if not command.strip():
        return {
            "blocked": True,
            "stdout": "",
            "stderr": "Empty AWS command",
            "returncode": 1,
        }

    try:
        parts = shlex.split(command)
    except ValueError as error:
        logger.exception("fetch_aws_account_info parse_failed command=%r", command)
        return {
            "blocked": True,
            "stdout": "",
            "stderr": str(error),
            "returncode": 1,
        }

    if not parts or parts[0] != "aws":
        logger.warning("fetch_aws_account_info blocked command=%r reason=not_aws", command)
        return {
            "blocked": True,
            "stdout": "",
            "stderr": "Only AWS CLI commands are allowed for this tool.",
            "returncode": 1,
        }

    if len(parts) < 2:
        logger.warning("fetch_aws_account_info blocked command=%r reason=incomplete", command)
        return {
            "blocked": True,
            "stdout": "",
            "stderr": "Incomplete AWS CLI command.",
            "returncode": 1,
        }

    service = parts[1]
    operation = parts[2] if len(parts) > 2 else ""
    is_s3_ls = service == "s3" and operation == "ls"
    is_read_only = operation.startswith(ALLOWED_AWS_ACTION_PREFIXES)
    is_sts_identity = service == "sts" and operation == "get-caller-identity"

    if not (is_s3_ls or is_read_only or is_sts_identity):
        logger.warning(
            "fetch_aws_account_info blocked command=%r service=%s operation=%s reason=non_read_only",
            command,
            service,
            operation,
        )
        return {
            "blocked": True,
            "stdout": "",
            "stderr": "Only read-only AWS CLI commands are allowed for this tool.",
            "returncode": 1,
        }

    logger.info("fetch_aws_account_info start command=%r service=%s operation=%s", command, service, operation)
    result = run_command(command)
    logger.info(
        "fetch_aws_account_info complete command=%r returncode=%s blocked=%s",
        command,
        result.get("returncode"),
        result.get("blocked"),
    )
    return result
