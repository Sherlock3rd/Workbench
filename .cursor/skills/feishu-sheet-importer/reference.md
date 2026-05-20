# Reference

## Directory Layout

```text
.cursor/skills/feishu-sheet-importer/
├── SKILL.md
├── README.md
├── reference.md
├── examples.md
├── config/
│   └── default-sheet-template.json
└── scripts/
    ├── check_import_prereqs.py
    ├── common.py
    ├── extract_workbook_images.py
    ├── import_excel_to_feishu_sheet.py
    └── apply_sheet_template.py
```

## First-Phase Contract
- Input: local `.xlsx`
- Output: Feishu `sheet`
- Placement: target Drive folder token
- Optional post-process: replay widths, title fills, header fills, bold fonts, and selected borders

## API Chain

### 1. Upload local source file
Default implementation uses:

```bash
lark-cli drive +upload --as user --file "<local.xlsx>" --name "<upload-name>"
```

Notes:
- This uploads a normal Drive file first.
- The script can delete that temporary uploaded file after import when `--cleanup-upload` is enabled.
- `drive +upload` currently documents a `20MB` limit in CLI help, so very large xlsx files may need a future `media/upload_all` path.

### 2. Create import task

```bash
lark-cli api POST /open-apis/drive/v1/import_tasks --as user --data '{
  "file_extension": "xlsx",
  "file_token": "<uploaded-file-token>",
  "type": "sheet",
  "file_name": "<target-title>",
  "point": {
    "mount_type": 1,
    "mount_key": "<folder-token>"
  }
}'
```

Official references:
- [导入文件概述](https://open.feishu.cn/document/server-docs/docs/drive-v1/import_task/import-user-guide)
- [创建导入任务](https://open.feishu.cn/document/server-docs/docs/drive-v1/import_task/create)

### 3. Poll import result

```bash
lark-cli api GET /open-apis/drive/v1/import_tasks/<ticket> --as user
```

Success shape:
- `data.result.job_status == 0`
- `data.result.token`
- `data.result.url`

Failure shape:
- `data.result.job_status != 0`
- `data.result.job_error_msg`

Official reference:
- [查询导入结果](https://open.feishu.cn/document/server-docs/docs/drive-v1/import_task/get)

### 4. Optional cleanup of uploaded source file

```bash
lark-cli api DELETE /open-apis/drive/v1/files/<file-token> --as user --params '{"type":"file"}'
```

Official reference:
- [删除文件或文件夹](https://open.feishu.cn/document/server-docs/docs/drive-v1/file/delete)

## Style Replay Strategy
The first-stage style replay is intentionally selective. It does not try to clone every Excel detail.

Current replay set:
- spreadsheet title
- first sheet title
- column widths
- row heights where the API accepts them
- bold/italic font
- foreground and background color
- left/center/right alignment where obvious
- full-border approximation when the source workbook uses visible borders
- optional merged cells
- embedded workbook images reinserted into target cells

Current non-goals:
- exact row height parity
- wrapped-text parity
- image anchoring parity
- formula or conditional-format parity

## Feishu Sheet Styling APIs Used
- Spreadsheet title patch:
  - `PATCH sheets.spreadsheets.patch`
- Sheet tab rename:
  - `POST /open-apis/sheets/v2/spreadsheets/:spreadsheetToken/sheets_batch_update`
- Column width:
  - `PUT /open-apis/sheets/v2/spreadsheets/:spreadsheetToken/dimension_range`
- Batch style update:
  - `PUT /open-apis/sheets/v2/spreadsheets/:spreadsheetToken/styles_batch_update`
- Merge cells:
  - `POST /open-apis/sheets/v2/spreadsheets/:spreadsheetToken/merge_cells`
- Write images:
  - `POST /open-apis/sheets/v2/spreadsheets/:spreadsheetToken/values_image`

Related docs:
- [Batch Set Cell Style](https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/batch-set-cell-style)
- [Merge Cells](https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/merge-cells)
- [Write Images](https://open.feishu.cn/document/ukTMukTMukTM/uUDNxYjL1QTM24SN0EjN)
- [Update sheet title summary](https://open.feishu.cn/document/ukTMukTMukTM/ugjMzUjL4IzM14COyMTN)

## Scope Matrix

| Action | Recommended scope |
| --- | --- |
| Upload local xlsx | `drive:file:upload` |
| Create import task | `docs:document:import` or `drive:drive` |
| Poll import result | `docs:document:import` or `drive:drive:readonly` |
| Rename spreadsheet / apply styles | `sheets:spreadsheet` or `drive:drive` |
| Delete temporary uploaded source file | `drive:drive` or `space:document:delete` |

If a user token is valid but these scopes are missing, the scripts should fail fast and report the missing API capability rather than silently retrying.

## Current Example Mapping
For `uxbench/output/kvktest_ux_text_requirements.xlsx`, the desired reading hierarchy comes from:
- `uxbench/output/kvktest_workbook_config.json`
- `.cursor/skills/ux-text-requirements-generator/scripts/build_ux_requirement_workbook.py`

Retain these visual semantics:
- `UI结构总览`
- chapter title rows
- left screenshot area
- middle interaction notes
- right `key / 内容 / 备注`
- light-blue title band and purple header band

## Future Extension Contract
The folder is designed so `html` and `doc` can be added without replacing the xlsx path:

1. keep `import_excel_to_feishu_sheet.py` as the xlsx adapter
2. add `import_html_to_sheet.py` or `import_doc_to_sheet.py`
3. keep post-import styling in `apply_sheet_template.py` or split it into a shared style module
4. keep one stable `SKILL.md` entry point
