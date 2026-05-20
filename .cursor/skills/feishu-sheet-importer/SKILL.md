---
name: feishu-sheet-importer
description: Import local excel, html, and doc-like files into Feishu documents, with xlsx converted into Feishu Sheets in a target folder and optionally restyled to match a review template. Use when the user mentions Excel, .xlsx, HTML, DOC, docx, 飞书 Sheet, 导入飞书表格, or wants local files converted and moved into a Feishu Drive folder.
---

# Feishu Sheet Importer

## Purpose
Convert local documents into Feishu-hosted docs with a stable automation flow. The current implemented path is:

1. local `.xlsx`
2. upload to Feishu
3. import as native Feishu `sheet`
4. place it in a specified Drive folder
5. replay key review styles when needed

This skill is stored under `.cursor/skills/feishu-sheet-importer/` with the other shared Cursor Skills in this workbench.

## Use When
- the user gives a local Excel file and wants it moved into Feishu
- the user says `飞书 Sheet` or `导入飞书表格`
- the user gives a Drive folder URL or folder token
- the user wants an existing review-style `.xlsx` converted into a collaborative Feishu spreadsheet
- the user later wants the same workflow expanded to `html`, `doc`, or `docx`

## Current Scope
- Implemented: `.xlsx` -> Feishu `sheet`
- Pre-reserved only: `html`, `doc`, `docx`
- Current default example file: `uxbench/output/kvktest_ux_text_requirements.xlsx`
- Current default target folder: use the folder token extracted from the user-provided Drive folder URL

## Required Preconditions
Before running the import flow:

1. Read `spec/feishu-cli-deployment-and-doc-ops-spec.md` if you need local project context.
2. Confirm `lark-cli config show` works.
3. Confirm `lark-cli auth status --verify` is valid.
4. Check scopes. The Excel import path needs:
   - `drive:file:upload`
   - `docs:document:import` or `drive:drive`
   - `sheets:spreadsheet` or `drive:drive` for style replay
5. Use `--as user` unless the user explicitly wants bot-owned files.

## Default Workflow
1. Confirm the local file path and target folder token.
2. If the user gives a folder URL, extract the `folder_token`.
3. Upload the local `.xlsx` with `lark-cli drive +upload`.
4. Create an import task with `POST /open-apis/drive/v1/import_tasks`.
5. Poll `GET /open-apis/drive/v1/import_tasks/:ticket` until the task is done.
6. If requested, clean up the uploaded source file so only the imported Sheet remains.
7. If the imported sheet lost key review styling, replay widths and key visual styles from the local workbook.
8. Return the imported spreadsheet URL, token, and any warnings.

## Preferred Commands
Run a preflight check before the first real import:

```bash
py -3 ".cursor/skills/feishu-sheet-importer/scripts/check_import_prereqs.py" --file "D:/path/to/file.xlsx"
```

Use the included scripts from this folder:

```bash
py -3 ".cursor/skills/feishu-sheet-importer/scripts/import_excel_to_feishu_sheet.py" --file "D:/path/to/file.xlsx" --folder-token "fld..." --apply-template --cleanup-upload
```

If only style replay is needed:

```bash
py -3 ".cursor/skills/feishu-sheet-importer/scripts/apply_sheet_template.py" --source-workbook "D:/path/to/file.xlsx" --spreadsheet "https://.../sheets/xxx"
```

## Output Expectations
For section-based review workbooks, preserve these semantics when possible:
- top `UI结构总览`
- chapter title rows
- left / middle / right visual grouping
- right-side `key / 内容 / 备注`
- title fills and header fills that preserve reading hierarchy

Do not promise pixel-perfect parity with Excel. The target is review readability, not exact renderer equivalence.

## Failure Handling
- If upload succeeds but import fails, report the import task payload.
- If import succeeds but style replay fails, return the spreadsheet URL plus the style warning.
- If missing scope blocks the flow, report the exact missing capability and stop guessing.
- If the user later asks for `html` or `doc`, keep the same folder layout and add a new input adapter instead of rewriting the xlsx path.

## Files In This Skill
- Detailed API notes and scope matrix: [reference.md](reference.md)
- Ready-to-copy usage examples: [examples.md](examples.md)
- Source style defaults: [config/default-sheet-template.json](config/default-sheet-template.json)
- Preflight check: [scripts/check_import_prereqs.py](scripts/check_import_prereqs.py)
- Import script: [scripts/import_excel_to_feishu_sheet.py](scripts/import_excel_to_feishu_sheet.py)
- Style replay script: [scripts/apply_sheet_template.py](scripts/apply_sheet_template.py)
