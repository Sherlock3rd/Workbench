from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import LarkCliError, run_command, run_lark_json


REQUIRED_SCOPES = [
    "drive:file:upload",
    "docs:document:import",
    "sheets:spreadsheet",
    "sheets:spreadsheet.meta:write_only",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check local and Feishu prerequisites for xlsx -> Sheet import.")
    parser.add_argument("--file", help="Optional local xlsx file to validate.")
    return parser.parse_args()


def check_scope(scope: str) -> dict:
    try:
        payload = run_lark_json(["auth", "check", "--scope", scope])
        return {"scope": scope, "ok": bool(payload.get("ok")), "payload": payload}
    except LarkCliError as exc:
        payload = {}
        try:
            payload = json.loads(exc.stdout or exc.stderr)
        except Exception:  # noqa: BLE001
            payload = {"error": str(exc)}
        return {"scope": scope, "ok": False, "payload": payload}


def main() -> None:
    args = parse_args()

    run_command(["py", "-3", "--version"])
    auth_status = run_lark_json(["auth", "status", "--verify"])

    file_info = None
    if args.file:
        file_path = Path(args.file).expanduser().resolve()
        if not file_path.exists():
            raise SystemExit(f"File not found: {file_path}")
        file_info = {
            "path": str(file_path),
            "suffix": file_path.suffix.lower(),
            "size_bytes": file_path.stat().st_size,
        }

    scope_results = [check_scope(scope) for scope in REQUIRED_SCOPES]
    result = {
        "python_ok": True,
        "auth_status": auth_status,
        "file_info": file_info,
        "scope_results": scope_results,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
