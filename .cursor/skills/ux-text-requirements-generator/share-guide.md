# Share Guide

## What To Share
For a teammate to reuse this workflow in Cursor, keep these files together:

- `.cursor/skills/ux-text-requirements-generator/README.md`
- `.cursor/skills/ux-text-requirements-generator/SKILL.md`
- `.cursor/skills/ux-text-requirements-generator/reference.md`
- `.cursor/skills/ux-text-requirements-generator/examples.md`
- `.cursor/skills/ux-text-requirements-generator/share-guide.md`
- `.cursor/skills/ux-text-requirements-generator/requirements.txt`
- `.cursor/skills/ux-text-requirements-generator/workbook_config_template.json`
- `.cursor/skills/ux-text-requirements-generator/scripts/_xlsx_reader.py`
- `.cursor/skills/ux-text-requirements-generator/scripts/bootstrap_env.ps1`
- `.cursor/skills/ux-text-requirements-generator/scripts/extract_sheet_schema.py`
- `.cursor/skills/ux-text-requirements-generator/scripts/extract_rule_hints.py`
- `.cursor/skills/ux-text-requirements-generator/scripts/prepare_prototype_manifest.py`
- `.cursor/skills/ux-text-requirements-generator/scripts/validate_requirement_rows.py`
- `tools/build_ux_requirement_workbook.py`

## Minimum Dependency Notes
Recommended Python packages:

```bash
py -3 -m pip install -r ".cursor/skills/ux-text-requirements-generator/requirements.txt"
```

If OCR is not available, the skill can still work with direct image reading plus manual review.

## Windows First-Run Setup
These commands are for project owners or fallback handling only.
External teammates should not be asked to run them manually if guided mode is working.

Recommended order on a clean machine:

1. Check Python:

```powershell
py -3 --version
```

2. If Python is missing:
- install Python 3 from python.org
- or run `winget install Python.Python.3.12`

3. Bootstrap packages:

```powershell
powershell -ExecutionPolicy Bypass -File ".cursor/skills/ux-text-requirements-generator/scripts/bootstrap_env.ps1"
```

4. Smoke test:

```powershell
py -3 ".cursor/skills/ux-text-requirements-generator/scripts/extract_sheet_schema.py" "文本需求案例.xlsx" --sheet "文本键值"
```

## Recommended Folder Strategy
This is a project skill, so the default location is:

```text
.cursor/skills/ux-text-requirements-generator/
```

Keep the workbook builder in:

```text
tools/build_ux_requirement_workbook.py
```

This separation is intentional:
- the skill folder stores instructions and reusable helper scripts
- the `tools` script handles the final screenshot-backed workbook build

## Starter Workflow
Before anything else, ask teammates to read:

```text
.cursor/skills/ux-text-requirements-generator/README.md
```

For external teammates, the preferred workflow is:
1. The teammate only provides the prototype image path in Cursor.
2. Cursor checks Python and dependencies automatically.
3. Cursor installs missing dependencies after one confirmation.
4. Cursor searches for project defaults for sample workbook and rule doc.
5. If no defaults exist, Cursor falls back to the built-in template and rule summary.
6. Cursor drafts chapters, fixes screenshot mapping, and builds the final workbook.

Only use the manual command below as a fallback:

```bash
py -3 "tools/build_ux_requirement_workbook.py" "tools/your_requirement_config.json"
```

## Packaging Advice
If you are sending this to another team:
- send the whole `.cursor/skills/ux-text-requirements-generator/` folder
- send `tools/build_ux_requirement_workbook.py`
- optionally send one polished example config, such as `tools/pet_growth_requirement_config_v12.json`
- optionally send one final workbook output as a visual reference

## Recommended Example Assets
Useful example deliverables from this repo:
- `tools/pet_growth_requirement_config_v12.json`
- `pet_growth_text_requirements_full_v12.xlsx`

## Maintenance Rules
- Keep keys semantic whenever possible.
- Prefer `TITLE / DESC / LABEL / BUTTON / HINT / VALUE / TAG`.
- Add a `UI结构总览` section before the first screenshot chapter for long UX flows.
- Split pages by `green title + arrow flow + same page different state`.
- Keep `备注` focused on location, trigger, and player-facing purpose.
- Fix screenshot mapping before polishing text rows.
- For each page, extract all user-facing text in the changed area, not just OCR-detected large headings.
