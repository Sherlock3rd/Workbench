# Feishu Sheet Importer

这个目录是一个 Cursor Skill 源码目录，目标是把本地文档转进飞书文档体系。当前已经落地的是第一阶段：

- 本地 `.xlsx`
- 导入为飞书 `Sheet`
- 放进指定云空间目录
- 按本地 Excel 的关键审阅样式做一次回放

## 当前实现

核心脚本：
- `scripts/check_import_prereqs.py`
- `scripts/import_excel_to_feishu_sheet.py`
- `scripts/apply_sheet_template.py`
- `scripts/extract_workbook_images.py`

关键文档：
- `SKILL.md`
- `reference.md`
- `examples.md`

## 适用场景

- 本地 Excel 需求文档转飞书 Sheet
- 需要保留章节感、表头层级、配色语义的审阅表
- 想把现有 Excel 协作链路迁移到飞书在线表格

## 当前限制

- 只正式实现了 `.xlsx`
- `html` / `doc` / `docx` 只做了结构预留
- 当前样式回放是“关键语义保留”，不是逐像素还原
- 很大的 Excel 仍可能受上传和导入限制影响
- 工作簿图片采用“提取后回灌”的方式补入飞书 Sheet，不完全依赖原生导入保留

## 下一步扩展建议

后续新增输入类型时，优先新增适配器脚本，而不是重写现有 xlsx 链路：

1. `import_html_to_sheet.py`
2. `import_doc_to_sheet.py`
3. 公共样式回放模块抽离
