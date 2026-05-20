from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
import zipfile
from xml.etree import ElementTree as ET

from _xlsx_reader import XlsxReader


KEY_PATTERN = re.compile(r"\b[A-Za-z0-9]+(?:[_\.-][A-Za-z0-9{}]+){1,}\b")
KEYWORD_PATTERN = re.compile(r"(key|命名|规范|前缀|后缀|页面|模块|按钮|标题)", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract likely key-naming rules and clue lines from docs."
    )
    parser.add_argument("sources", nargs="+", help="Paths to .md/.txt/.xlsx files")
    parser.add_argument(
        "--line-limit",
        type=int,
        default=80,
        help="Max clue lines to keep in the final report.",
    )
    return parser.parse_args()


def read_source(path: Path) -> list[str]:
    suffix = path.suffix.lower()
    if suffix == ".xlsx":
        reader = XlsxReader(path)
        try:
            return reader.iter_all_strings()
        finally:
            reader.close()
    if suffix == ".docx":
        archive = zipfile.ZipFile(path)
        root = ET.fromstring(archive.read("word/document.xml"))
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        lines = []
        for paragraph in root.findall(".//w:p", ns):
            texts = [node.text or "" for node in paragraph.findall(".//w:t", ns)]
            line = "".join(texts).strip()
            if line:
                lines.append(line)
        archive.close()
        return lines
    return path.read_text(encoding="utf-8", errors="ignore").splitlines()


def infer_case_style(candidates: list[str]) -> str:
    if not candidates:
        return "unknown"
    alpha_only = [value for value in candidates if re.search(r"[A-Za-z]", value)]
    if alpha_only and all(value.upper() == value for value in alpha_only):
        return "uppercase"
    if all(value.lower() == value for value in candidates):
        return "lowercase"
    return "mixed"


def infer_separator(counter: Counter[str]) -> str:
    if not counter:
        return "unknown"
    return counter.most_common(1)[0][0]


def recommend_regex(separator: str, case_style: str) -> str:
    if separator == "_":
        token = "[a-z0-9]+" if case_style == "lowercase" else "[A-Za-z0-9]+"
        return rf"^{token}(?:_{token})+$"
    if separator == ".":
        token = "[a-z0-9]+" if case_style == "lowercase" else "[A-Za-z0-9]+"
        return rf"^{token}(?:\.{token})+$"
    if separator == "-":
        token = "[a-z0-9]+" if case_style == "lowercase" else "[A-Za-z0-9]+"
        return rf"^{token}(?:-{token})+$"
    return r"^[A-Za-z0-9._-]+$"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    clue_lines: list[dict[str, str]] = []
    key_examples: list[str] = []
    separator_counter: Counter[str] = Counter()
    seen_clue_pairs: set[tuple[str, str]] = set()
    all_lines: list[str] = []

    for raw_source in args.sources:
        path = Path(raw_source)
        if not path.exists():
            clue_lines.append({"source": str(path), "line": "[missing file]"})
            continue

        for line in read_source(path):
            cleaned = " ".join(line.replace("\r", "\n").split())
            if not cleaned:
                continue
            all_lines.append(cleaned)

            if KEYWORD_PATTERN.search(cleaned):
                pair = (str(path), cleaned)
                if pair not in seen_clue_pairs:
                    seen_clue_pairs.add(pair)
                    clue_lines.append({"source": str(path), "line": cleaned})

            for key in KEY_PATTERN.findall(cleaned):
                key_examples.append(key)
                if "_" in key:
                    separator_counter["_"] += 1
                if "." in key:
                    separator_counter["."] += 1
                if "-" in key:
                    separator_counter["-"] += 1

    unique_examples = list(dict.fromkeys(key_examples))[:40]
    case_style = infer_case_style(unique_examples)
    separator = infer_separator(separator_counter)
    recommended_columns = []
    if {"TAB", "KEY", "功能模块"}.issubset(set(all_lines)):
        recommended_columns = ["TAB", "KEY", "文本", "功能模块", "备注", "Max_Length"]
    key_structure = ""
    if "[TAB] + [SUBTAB] + [ID] + [TYPE]" in all_lines:
        key_structure = "[TAB] + [SUBTAB] + [ID] + [TYPE]"
    special_rules = []
    for line in all_lines:
        if "不要把ID写在最后面" in line:
            special_rules.append("ID must stay in the middle of the key, not at the end.")
        if "错误码" in line and "备注" in line:
            special_rules.append("Error and prompt text may use existing keys, but remarks are mandatory and must describe the trigger condition.")
        if "不允许出现“对话”" in line or "不要出现“对话”" in line:
            special_rules.append("The 功能模块 field must not contain the word 对话.")
        if "{p1}" in line and "{Num}" in line:
            special_rules.append("Prefer semantic rich-text placeholders such as {Num} instead of generic placeholders like {p1}.")
        if "最长字符数限制" in line:
            special_rules.append("Long text or special UI text should include a max length confirmation.")

    payload = {
        "sources": args.sources,
        "key_structure": key_structure,
        "candidate_keys": unique_examples,
        "separator_counts": dict(separator_counter),
        "inferred_separator": separator,
        "inferred_case_style": case_style,
        "recommended_regex": recommend_regex(separator, case_style),
        "recommended_columns": recommended_columns,
        "special_rules": list(dict.fromkeys(special_rules)),
        "clue_lines": clue_lines[: args.line_limit],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
