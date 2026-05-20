from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from json import JSONDecoder
from pathlib import Path
from typing import Any, Iterable, Sequence


class LarkCliError(RuntimeError):
    """Raised when a lark-cli command fails or returns an API error."""

    def __init__(self, message: str, *, stdout: str = "", stderr: str = "", exit_code: int | None = None) -> None:
        super().__init__(message)
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code


@dataclass(frozen=True)
class SheetRef:
    sheet_id: str
    title: str | None = None


def run_command(args: Sequence[str], *, cwd: Path | None = None) -> str:
    resolved_args = list(args)
    executable = shutil.which(resolved_args[0])
    if executable is None and sys.platform.startswith("win") and "." not in Path(resolved_args[0]).name:
        for suffix in (".cmd", ".exe", ".bat"):
            executable = shutil.which(resolved_args[0] + suffix)
            if executable:
                break
    if executable:
        resolved_args[0] = executable

    completed = subprocess.run(
        resolved_args,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    stdout = (completed.stdout or "").strip()
    stderr = (completed.stderr or "").strip()
    if completed.returncode != 0:
        message = stderr or stdout or f"Command failed: {' '.join(resolved_args)}"
        raise LarkCliError(message, stdout=stdout, stderr=stderr, exit_code=completed.returncode)
    return stdout


def parse_json_output(text: str) -> Any:
    stripped = text.strip()
    if not stripped:
        raise ValueError("Command returned empty output; expected JSON.")

    decoder = JSONDecoder()
    for idx, char in enumerate(stripped):
        if char not in "[{":
            continue
        try:
            parsed, _ = decoder.raw_decode(stripped[idx:])
            return parsed
        except json.JSONDecodeError:
            continue
    raise ValueError(f"Could not find JSON in command output:\n{stripped}")


def run_lark_json(args: Sequence[str], *, cwd: Path | None = None) -> Any:
    return parse_json_output(run_command(["lark-cli", *args], cwd=cwd))


def ensure_lark_success(payload: Any) -> Any:
    if isinstance(payload, dict) and "code" in payload and payload.get("code") not in (0, "0", None):
        raise LarkCliError(
            f"Lark API returned code={payload.get('code')}: {payload.get('msg', 'unknown error')}",
            stdout=json.dumps(payload, ensure_ascii=False, indent=2),
        )
    return payload


def extract_spreadsheet_token(token_or_url: str) -> str:
    value = token_or_url.strip()
    if "://" not in value:
        return value

    match = re.search(r"/sheets/([A-Za-z0-9]+)", value)
    if not match:
        raise ValueError(f"Could not extract spreadsheet token from URL: {token_or_url}")
    return match.group(1)


def deep_find_sheet_refs(node: Any) -> list[SheetRef]:
    refs: list[SheetRef] = []

    if isinstance(node, dict):
        sheet_id = node.get("sheet_id") or node.get("sheetId")
        if isinstance(sheet_id, str):
            title = node.get("title")
            refs.append(SheetRef(sheet_id=sheet_id, title=title if isinstance(title, str) else None))
        for value in node.values():
            refs.extend(deep_find_sheet_refs(value))
    elif isinstance(node, list):
        for item in node:
            refs.extend(deep_find_sheet_refs(item))

    deduped: dict[str, SheetRef] = {}
    for ref in refs:
        deduped[ref.sheet_id] = ref
    return list(deduped.values())


def pick_sheet_ref(info_payload: Any, preferred_title: str | None = None) -> SheetRef:
    refs = deep_find_sheet_refs(info_payload)
    if not refs:
        raise ValueError("Could not locate any sheet_id in spreadsheet info payload.")
    if preferred_title:
        for ref in refs:
            if ref.title == preferred_title:
                return ref
    return refs[0]


def excel_width_to_pixels(width: float | None) -> int | None:
    if width is None:
        return None
    if width <= 0:
        return 0
    return int(round(width * 7 + 5))


def hex_color_from_openpyxl(color: Any) -> str | None:
    if color is None:
        return None
    if getattr(color, "type", None) not in (None, "rgb"):
        return None
    rgb = getattr(color, "rgb", None)
    if not isinstance(rgb, str) or not rgb:
        return None
    if len(rgb) == 8:
        rgb = rgb[2:]
    if len(rgb) != 6:
        return None
    return f"#{rgb.upper()}"


def chunk_consecutive(items: Iterable[tuple[int, int]]) -> list[tuple[int, int, int]]:
    """Convert sorted (index, value) pairs to (start, end, value) groups."""
    groups: list[tuple[int, int, int]] = []
    start: int | None = None
    end: int | None = None
    current_value: int | None = None

    for index, value in items:
        if start is None:
            start = end = index
            current_value = value
            continue
        if index == end + 1 and value == current_value:
            end = index
            continue
        groups.append((start, end, current_value))  # type: ignore[arg-type]
        start = end = index
        current_value = value

    if start is not None and end is not None and current_value is not None:
        groups.append((start, end, current_value))
    return groups
