from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import zipfile
import xml.etree.ElementTree as ET


MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"a": MAIN_NS, "r": REL_NS}
CELL_REF_RE = re.compile(r"([A-Z]+)(\d+)")


def column_letter_to_index(column_letters: str) -> int:
    result = 0
    for char in column_letters:
        result = result * 26 + (ord(char) - ord("A") + 1)
    return result


def normalize_cell_text(value: str) -> str:
    return " ".join((value or "").replace("\r", "\n").split())


@dataclass
class SheetData:
    name: str
    target: str
    rows: list[dict[int, str]]
    max_row: int
    max_col: int

    def row_values(self, row_number: int, upto_col: int | None = None) -> list[str]:
        row = self.rows[row_number - 1] if 0 < row_number <= len(self.rows) else {}
        limit = upto_col or self.max_col
        return [row.get(index, "") for index in range(1, limit + 1)]


class XlsxReader:
    def __init__(self, workbook_path: str | Path) -> None:
        self.workbook_path = Path(workbook_path)
        self.archive = zipfile.ZipFile(self.workbook_path)
        self.shared_strings = self._load_shared_strings()
        self.sheet_targets = self._load_sheet_targets()

    def close(self) -> None:
        self.archive.close()

    def _load_shared_strings(self) -> list[str]:
        if "xl/sharedStrings.xml" not in self.archive.namelist():
            return []

        root = ET.fromstring(self.archive.read("xl/sharedStrings.xml"))
        strings: list[str] = []
        for node in root.findall("a:si", NS):
            text_parts = [part.text or "" for part in node.findall(".//a:t", NS)]
            strings.append("".join(text_parts))
        return strings

    def _load_sheet_targets(self) -> list[tuple[str, str]]:
        workbook_root = ET.fromstring(self.archive.read("xl/workbook.xml"))
        rel_root = ET.fromstring(self.archive.read("xl/_rels/workbook.xml.rels"))
        rel_map = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in rel_root.findall(f"{{{PKG_REL_NS}}}Relationship")
        }
        sheet_targets: list[tuple[str, str]] = []
        for sheet in workbook_root.findall("a:sheets/a:sheet", NS):
            rel_id = sheet.attrib[f"{{{REL_NS}}}id"]
            target = rel_map[rel_id].replace("\\", "/")
            if not target.startswith("xl/"):
                target = f"xl/{target}"
            sheet_targets.append((sheet.attrib["name"], target))
        return sheet_targets

    def list_sheets(self) -> list[str]:
        return [name for name, _target in self.sheet_targets]

    def read_sheet(self, sheet_name: str) -> SheetData:
        target = None
        for candidate_name, candidate_target in self.sheet_targets:
            if candidate_name == sheet_name:
                target = candidate_target
                break
        if target is None:
            raise KeyError(f"Unknown sheet: {sheet_name}")

        sheet_root = ET.fromstring(self.archive.read(target))
        rows: list[dict[int, str]] = []
        max_col = 0
        max_row = 0

        for row_node in sheet_root.findall("a:sheetData/a:row", NS):
            row_number = int(row_node.attrib.get("r", len(rows) + 1))
            row_map: dict[int, str] = {}
            for cell in row_node.findall("a:c", NS):
                ref = cell.attrib.get("r", "")
                match = CELL_REF_RE.match(ref)
                if not match:
                    continue
                col_index = column_letter_to_index(match.group(1))
                row_map[col_index] = self._read_cell_value(cell)
                max_col = max(max_col, col_index)
            while len(rows) < row_number - 1:
                rows.append({})
            rows.append(row_map)
            max_row = max(max_row, row_number)

        return SheetData(
            name=sheet_name,
            target=target,
            rows=rows,
            max_row=max_row,
            max_col=max_col,
        )

    def iter_all_strings(self) -> list[str]:
        seen: list[str] = []
        for sheet_name in self.list_sheets():
            sheet = self.read_sheet(sheet_name)
            for row in sheet.rows:
                for value in row.values():
                    cleaned = normalize_cell_text(value)
                    if cleaned:
                        seen.append(cleaned)
        return seen

    def _read_cell_value(self, cell: ET.Element) -> str:
        cell_type = cell.attrib.get("t")
        value_node = cell.find("a:v", NS)

        if cell_type == "s" and value_node is not None:
            index = int(value_node.text or "0")
            return self.shared_strings[index] if 0 <= index < len(self.shared_strings) else ""

        if cell_type == "inlineStr":
            text_parts = [part.text or "" for part in cell.findall(".//a:t", NS)]
            return "".join(text_parts)

        if cell_type == "b" and value_node is not None:
            return "TRUE" if value_node.text == "1" else "FALSE"

        if value_node is not None and value_node.text is not None:
            return value_node.text

        formula_node = cell.find("a:f", NS)
        if formula_node is not None and formula_node.text is not None:
            return f"={formula_node.text}"

        return ""
