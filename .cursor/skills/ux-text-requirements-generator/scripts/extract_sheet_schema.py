from __future__ import annotations

import argparse
import json
from pathlib import Path

from _xlsx_reader import XlsxReader, normalize_cell_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect an xlsx workbook and infer a header-oriented schema."
    )
    parser.add_argument("workbook", help="Path to the .xlsx workbook")
    parser.add_argument("--sheet", help="Sheet name. Defaults to the first sheet.")
    parser.add_argument(
        "--sample-rows",
        type=int,
        default=12,
        help="Number of rows to include around the inferred header.",
    )
    return parser.parse_args()


def infer_header_row(sheet_rows: list[dict[int, str]], max_scan_rows: int) -> int:
    best_row = 1
    best_score = (-1, -1)

    for row_number, row in enumerate(sheet_rows[:max_scan_rows], start=1):
        non_empty = [normalize_cell_text(value) for value in row.values() if normalize_cell_text(value)]
        if len(non_empty) < 2:
            continue
        unique_cells = len(set(non_empty))
        score = (unique_cells, len(non_empty))
        if score > best_score:
            best_score = score
            best_row = row_number

    return best_row


def build_schema_payload(workbook_path: Path, sheet_name: str, sample_rows: int) -> dict:
    reader = XlsxReader(workbook_path)
    try:
        target_sheet = sheet_name or reader.list_sheets()[0]
        sheet = reader.read_sheet(target_sheet)
    finally:
        reader.close()

    header_row_number = infer_header_row(sheet.rows, max_scan_rows=min(20, max(5, sample_rows + 4)))
    header_values = sheet.row_values(header_row_number)
    columns = []
    for index, value in enumerate(header_values, start=1):
        cleaned = normalize_cell_text(value)
        if cleaned:
            columns.append({"index": index, "name": cleaned})

    sample = []
    last_row = min(sheet.max_row, header_row_number + sample_rows)
    for row_number in range(header_row_number + 1, last_row + 1):
        row_values = sheet.row_values(row_number, upto_col=sheet.max_col)
        if not any(normalize_cell_text(value) for value in row_values):
            continue
        sample.append(
            {
                "row_number": row_number,
                "values": {
                    column["name"]: normalize_cell_text(row_values[column["index"] - 1])
                    for column in columns
                },
            }
        )

    return {
        "workbook": str(workbook_path),
        "sheet_name": sheet.name,
        "sheet_target": sheet.target,
        "sheet_dimensions": {"max_row": sheet.max_row, "max_col": sheet.max_col},
        "inferred_header_row": header_row_number,
        "columns": columns,
        "sample_rows": sample,
    }


def main() -> int:
    args = parse_args()
    payload = build_schema_payload(Path(args.workbook), args.sheet, args.sample_rows)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
