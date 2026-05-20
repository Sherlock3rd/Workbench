from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from common import LarkCliError, ensure_lark_success, extract_spreadsheet_token, run_lark_json


SUCCESS_STATUS = 0
PENDING_STATUSES = {1, 2}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import a local xlsx file into a Feishu spreadsheet.")
    parser.add_argument("--file", required=True, help="Local xlsx file path.")
    parser.add_argument("--folder-token", required=True, help="Destination Feishu Drive folder token.")
    parser.add_argument("--identity", default="user", choices=["user", "bot"], help="lark-cli identity.")
    parser.add_argument("--file-name", help="Imported spreadsheet title. Defaults to the local file stem.")
    parser.add_argument(
        "--upload-name",
        help="Temporary upload file name used before import. Defaults to the local file name.",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=2.0,
        help="Seconds between import status polls.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=180.0,
        help="Maximum seconds to wait for import completion.",
    )
    parser.add_argument(
        "--cleanup-upload",
        action="store_true",
        help="Delete the uploaded source file after import succeeds.",
    )
    parser.add_argument(
        "--apply-template",
        action="store_true",
        help="Replay key styles from the source workbook onto the imported sheet.",
    )
    parser.add_argument(
        "--copy-merges",
        action="store_true",
        help="When applying the template, also replay merged ranges from the source workbook.",
    )
    parser.add_argument(
        "--skip-template-errors",
        action="store_true",
        help="Do not fail the import if the style replay step hits a recoverable API issue.",
    )
    return parser.parse_args()


def upload_source_file(file_path: Path, upload_name: str, identity: str) -> tuple[str, dict]:
    payload = ensure_lark_success(
        run_lark_json(
            [
                "drive",
                "+upload",
                "--as",
                identity,
                "--file",
                file_path.name,
                "--name",
                upload_name,
            ],
            cwd=file_path.parent,
        )
    )

    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        raise LarkCliError("Unexpected upload response shape.", stdout=json.dumps(payload, ensure_ascii=False, indent=2))

    file_token = data.get("file_token") or data.get("token")
    if not isinstance(file_token, str):
        raise LarkCliError("Could not find file_token in upload response.", stdout=json.dumps(payload, ensure_ascii=False, indent=2))
    return file_token, payload


def create_import_task(
    file_token: str,
    folder_token: str,
    file_extension: str,
    file_name: str,
    identity: str,
) -> str:
    body = {
        "file_extension": file_extension,
        "file_token": file_token,
        "type": "sheet",
        "file_name": file_name,
        "point": {
            "mount_type": 1,
            "mount_key": folder_token,
        },
    }
    payload = ensure_lark_success(
        run_lark_json(
            [
                "api",
                "POST",
                "/open-apis/drive/v1/import_tasks",
                "--as",
                identity,
                "--data",
                json.dumps(body, ensure_ascii=False),
            ]
        )
    )
    ticket = (((payload.get("data") or {}) if isinstance(payload, dict) else {}).get("ticket"))
    if not isinstance(ticket, str):
        raise LarkCliError("Could not find import ticket in response.", stdout=json.dumps(payload, ensure_ascii=False, indent=2))
    return ticket


def poll_import_result(ticket: str, identity: str, poll_interval: float, timeout: float) -> dict:
    deadline = time.time() + timeout
    last_payload: dict | None = None
    while time.time() < deadline:
        payload = ensure_lark_success(
            run_lark_json(
                [
                    "api",
                    "GET",
                    f"/open-apis/drive/v1/import_tasks/{ticket}",
                    "--as",
                    identity,
                ]
            )
        )
        last_payload = payload if isinstance(payload, dict) else None
        result = ((payload.get("data") or {}) if isinstance(payload, dict) else {}).get("result")
        if not isinstance(result, dict):
            raise LarkCliError("Could not find import result payload.", stdout=json.dumps(payload, ensure_ascii=False, indent=2))

        job_status = result.get("job_status")
        if job_status in PENDING_STATUSES:
            time.sleep(poll_interval)
            continue
        if job_status != SUCCESS_STATUS:
            raise LarkCliError(
                f"Import failed with job_status={job_status}: {result.get('job_error_msg', 'unknown error')}",
                stdout=json.dumps(payload, ensure_ascii=False, indent=2),
            )
        return result

    raise TimeoutError(json.dumps(last_payload, ensure_ascii=False, indent=2) if last_payload else "Import polling timed out.")


def cleanup_uploaded_file(file_token: str, identity: str) -> dict:
    return ensure_lark_success(
        run_lark_json(
            [
                "api",
                "DELETE",
                f"/open-apis/drive/v1/files/{file_token}",
                "--as",
                identity,
                "--params",
                json.dumps({"type": "file"}, ensure_ascii=False),
            ]
        )
    )


def apply_template(file_path: Path, spreadsheet_token: str, file_name: str, identity: str, copy_merges: bool) -> dict:
    script_path = Path(__file__).with_name("apply_sheet_template.py")
    command = [
        sys.executable,
        str(script_path),
        "--source-workbook",
        str(file_path),
        "--spreadsheet",
        spreadsheet_token,
        "--identity",
        identity,
        "--spreadsheet-title",
        file_name,
        "--copy-merges",
        "--insert-images",
    ]
    if not copy_merges:
        command.remove("--copy-merges")

    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise LarkCliError(
            "Template replay failed.",
            stdout=completed.stdout.strip(),
            stderr=completed.stderr.strip(),
            exit_code=completed.returncode,
        )
    return json.loads(completed.stdout)


def main() -> None:
    args = parse_args()
    file_path = Path(args.file).expanduser().resolve()
    if not file_path.exists():
        raise SystemExit(f"File not found: {file_path}")
    if file_path.suffix.lower() != ".xlsx":
        raise SystemExit("This script currently supports only .xlsx input.")

    file_name = args.file_name or file_path.stem
    upload_name = args.upload_name or file_path.name

    file_token, upload_payload = upload_source_file(file_path, upload_name, args.identity)
    ticket = create_import_task(
        file_token=file_token,
        folder_token=args.folder_token,
        file_extension=file_path.suffix.lower().lstrip("."),
        file_name=file_name,
        identity=args.identity,
    )
    result = poll_import_result(ticket, args.identity, args.poll_interval, args.timeout)
    spreadsheet_token = extract_spreadsheet_token(result["token"])

    cleanup_result = None
    if args.cleanup_upload:
        cleanup_result = cleanup_uploaded_file(file_token, args.identity)

    template_result = None
    if args.apply_template:
        try:
            template_result = apply_template(
                file_path=file_path,
                spreadsheet_token=spreadsheet_token,
                file_name=file_name,
                identity=args.identity,
                copy_merges=args.copy_merges,
            )
        except Exception as exc:  # noqa: BLE001
            if not args.skip_template_errors:
                raise
            template_result = {"warning": str(exc)}

    summary = {
        "uploaded_file_token": file_token,
        "upload_response": upload_payload,
        "ticket": ticket,
        "import_result": result,
        "cleanup_result": cleanup_result,
        "template_result": template_result,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
