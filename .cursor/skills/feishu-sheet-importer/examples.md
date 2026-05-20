# Examples

## Example 0: Preflight check

```bash
py -3 ".cursor/skills/feishu-sheet-importer/scripts/check_import_prereqs.py" \
  --file "D:/charlie/Workbencch/uxbench/output/kvktest_ux_text_requirements.xlsx"
```

Use this when:
- you want to verify Python, Feishu login, file size, and required scopes first
- you suspect the flow will be blocked by missing import or sheet-write permissions

## Example 1: Import the current kvktest workbook

```bash
py -3 ".cursor/skills/feishu-sheet-importer/scripts/import_excel_to_feishu_sheet.py" \
  --file "D:/charlie/Workbencch/uxbench/output/kvktest_ux_text_requirements.xlsx" \
  --folder-token "XrVMfgT6qlu7oHdRV11ca3wSn6H" \
  --apply-template \
  --cleanup-upload
```

Expected outcome:
- a new Feishu spreadsheet appears in the target folder
- the spreadsheet title defaults to `kvktest_ux_text_requirements`
- key review styles are replayed from the local workbook

## Example 2: Import but keep the uploaded source file

```bash
py -3 ".cursor/skills/feishu-sheet-importer/scripts/import_excel_to_feishu_sheet.py" \
  --file "D:/charlie/Workbencch/uxbench/output/kvktest_ux_text_requirements.xlsx" \
  --folder-token "XrVMfgT6qlu7oHdRV11ca3wSn6H"
```

Use this when:
- you want a visible archival copy of the original xlsx in Drive
- cleanup permission is not available

## Example 3: Replay template only

```bash
py -3 ".cursor/skills/feishu-sheet-importer/scripts/apply_sheet_template.py" \
  --source-workbook "D:/charlie/Workbencch/uxbench/output/kvktest_ux_text_requirements.xlsx" \
  --spreadsheet "https://t6bdpf8yjg.feishu.cn/sheets/<spreadsheet-token>" \
  --copy-merges \
  --insert-images
```

Use this when:
- the xlsx import already succeeded
- the imported Feishu sheet kept the data but lost parts of the review hierarchy

## Example 3.1: Extract workbook images before manual or staged replay

```bash
py -3 ".cursor/skills/feishu-sheet-importer/scripts/extract_workbook_images.py" \
  --source-workbook "D:/charlie/Workbencch/uxbench/output/kvktest_ux_text_requirements.xlsx" \
  --output-dir "D:/charlie/Workbencch/.cursor/skills/feishu-sheet-importer/tmp/kvktest_images"
```

Use this when:
- you need to inspect the original workbook screenshots
- you want an explicit manifest of image file -> target cell

## Example 4: Safer import when style replay may partially fail

```bash
py -3 ".cursor/skills/feishu-sheet-importer/scripts/import_excel_to_feishu_sheet.py" \
  --file "D:/charlie/Workbencch/uxbench/output/kvktest_ux_text_requirements.xlsx" \
  --folder-token "XrVMfgT6qlu7oHdRV11ca3wSn6H" \
  --apply-template \
  --skip-template-errors \
  --cleanup-upload
```

Use this when:
- import success matters more than formatting completeness
- the current Feishu app scopes for `sheets:spreadsheet` are still being prepared
