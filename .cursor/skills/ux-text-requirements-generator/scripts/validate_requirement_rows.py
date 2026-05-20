from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate sheet-like requirement output before pasting into Feishu Excel."
    )
    parser.add_argument("input_file", help="Path to a .json, .csv, or .tsv file")
    parser.add_argument(
        "--required-columns",
        default="",
        help="Comma-separated required columns. Example: 页面名,文案key,显示文本",
    )
    parser.add_argument(
        "--key-column-candidates",
        default="文案key,key,text_key,i18n_key",
        help="Comma-separated key column names to probe in order.",
    )
    parser.add_argument(
        "--page-column-candidates",
        default="页面名,page_name,页面,page",
        help="Comma-separated page column names to probe in order.",
    )
    parser.add_argument(
        "--key-regex",
        default="",
        help="Regex used to validate key values.",
    )
    return parser.parse_args()


def load_rows(input_path: Path) -> list[dict[str, str]]:
    suffix = input_path.suffix.lower()
    if suffix == ".json":
        data = json.loads(input_path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [{str(k): str(v) for k, v in row.items()} for row in data]
        raise ValueError("JSON input must be a list of objects.")

    delimiter = "\t" if suffix == ".tsv" else ","
    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def pick_column(rows: list[dict[str, str]], candidates: list[str]) -> str | None:
    if not rows:
        return None
    headers = set(rows[0].keys())
    for candidate in candidates:
        if candidate in headers:
            return candidate
    return None


def main() -> int:
    args = parse_args()
    rows = load_rows(Path(args.input_file))
    required_columns = [column.strip() for column in args.required_columns.split(",") if column.strip()]
    errors: list[str] = []
    warnings: list[str] = []

    if not rows:
        errors.append("No rows were found in the input file.")
        print(json.dumps({"errors": errors, "warnings": warnings}, ensure_ascii=False, indent=2))
        return 1

    headers = list(rows[0].keys())
    for column in required_columns:
        if column not in headers:
            errors.append(f"Missing required column: {column}")

    key_column = pick_column(rows, [value.strip() for value in args.key_column_candidates.split(",")])
    page_column = pick_column(rows, [value.strip() for value in args.page_column_candidates.split(",")])

    key_regex = re.compile(args.key_regex) if args.key_regex else None
    seen_keys: dict[str, int] = {}

    for index, row in enumerate(rows, start=2):
        if page_column and not (row.get(page_column) or "").strip():
            warnings.append(f"Row {index}: empty page name")

        if key_column:
            key_value = (row.get(key_column) or "").strip()
            if not key_value:
                warnings.append(f"Row {index}: empty key")
            else:
                seen_keys[key_value] = seen_keys.get(key_value, 0) + 1
                if key_regex and not key_regex.fullmatch(key_value):
                    warnings.append(f"Row {index}: key does not match regex -> {key_value}")

    duplicate_keys = sorted([key for key, count in seen_keys.items() if count > 1])
    for key in duplicate_keys:
        warnings.append(f"Duplicate key: {key}")

    payload = {
        "headers": headers,
        "row_count": len(rows),
        "key_column": key_column,
        "page_column": page_column,
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
