---
name: ux-text-requirements-generator
description: Generate Feishu Excel-ready UX text requirement drafts from a prototype image, a sample requirement workbook, and key naming rules. Use when the user provides UX mockups, long stitched prototype images, text requirement examples, localization key sheets, or asks to turn UI images into page-by-page text requirement docs.
---

# UX Text Requirements Generator

## Purpose
Convert a UX prototype image into a page-by-page text requirement draft that matches the team's historical Excel structure and key naming style.

The default authoring perspective is `系统策划提给文案策划`, so page notes should explain:
- where the player enters
- what interaction triggers the copy
- where the copy appears in the UI
- what player-facing purpose the copy serves

## Use When
- the user gives a `UX 原型图` or a long stitched mockup
- the user wants `文本需求`, `文案需求`, or `飞书 Excel` output
- the user provides a sample `.xlsx` and asks to follow its format
- the user provides `key` naming rules or a localization sheet

## Inputs
- `prototype image`: one long image is the default case
- `sample workbook`: historical requirement sheet or text key sheet
- `rule doc`: key naming rules, terminology, prefixes, suffixes, or page/module naming conventions

If one input is missing, proceed with the available inputs and mark assumptions explicitly.

## Guided Mode
When this skill is used for teammates, default to a fully guided Cursor workflow:
1. If the user only provides the UX image path, do not ask them to run terminal commands manually.
2. Use `AskQuestion` to guide missing decisions with simple choices.
3. Proactively check Python and dependencies yourself.
4. If installation is needed, ask for confirmation once, then run the install steps yourself.
5. If no sample workbook or rule doc is provided:
   - search the workspace for likely defaults first
   - if none are found, fall back to the built-in template and the Beagle rule summary in this skill
   - clearly mark that the result is based on default project heuristics
6. The teammate should only need to:
   - provide the UX prototype image path
   - confirm installation or output choices when prompted

## Environment Setup
If Python or required packages are missing, install them before running any helper script:
1. On Windows, check Python first:
   - `py -3 --version`
2. If Python is missing:
   - install Python 3 from python.org or `winget install Python.Python.3.12`
3. Then bootstrap the local environment:
   - `powershell -ExecutionPolicy Bypass -File ".cursor/skills/ux-text-requirements-generator/scripts/bootstrap_env.ps1"`
4. If the environment still cannot be prepared:
   - continue with model vision
   - produce a normalized draft first
   - mark script-dependent verification as skipped

In guided mode, the agent should run these steps itself after user confirmation rather than telling the user to do them manually.

## Default Workflow
0. If the user only gave a prototype image path, start guided intake:
   - confirm the image path
   - ask whether to auto-install missing dependencies
   - ask whether to use default built-in template/rules if no project files are found
1. Learn the output structure from the sample workbook.
   - Run `scripts/extract_sheet_schema.py "<sample.xlsx>" --sheet "<target_sheet>"`
   - If the workbook has multiple sheets, inspect them first and choose the text-requirement-like sheet
2. Learn key rules from the rule doc and the sample workbook.
   - Run `scripts/extract_rule_hints.py "<rule_doc>" "<sample.xlsx>"`
   - Prefer the user's explicit rule doc over inferred examples
   - If the rule doc is the Beagle 7-day simplified standard, treat it as a hard rule set:
     - key structure is `[TAB] + [SUBTAB] + [ID] + [TYPE]`
     - batch columns are `TAB`, `KEY`, `文本`, `功能模块`, `备注`, `Max_Length`
3. Pre-split the prototype image into candidate page blocks.
   - Run `scripts/prepare_prototype_manifest.py "<prototype.png>" --ocr none`
   - If Pillow is unavailable, continue with manual visual reading
4. Read the image directly with model vision and label each block as:
   - `page`
   - `popup`
   - `drawer`
   - `tab state`
   - `mode switch`
   - `annotation`
5. Build the intermediate structure before drafting rows:
   - `PageNode`
   - `TextElement`
   - `RequirementRow`
6. Generate the final output in the sample's structure.
   - Preserve the sample column order when the sheet is column-based
   - Preserve page-title grouping when the sheet is section-based
   - Keep uncertain items marked as `待确认`
   - When the user wants a final deliverable, prefer a `top UI structure overview + left screenshot + middle interaction notes + right key/content/remark` Excel workbook
7. Validate before finalizing.
   - If the output is row-based JSON/CSV/TSV, run `scripts/validate_requirement_rows.py`

## Current Stable Workflow
Use this stronger workflow when the prototype is a large stitched UX flow:
1. Choose one high-resolution source image as the primary crop source.
2. Build all page crop boxes against one shared coordinate system when possible.
3. Split pages by:
   - green title
   - arrow direction
   - same page different state
4. Do not split one UX node into multiple chapters unless the screenshot clearly represents a new state.
5. Add a UI overview section at the top of the workbook before the page-by-page requirement chapters.
6. After screenshot logic is stable, refine text requirements page by page.

## How To Decide Which Text To Extract
For each page, think like `系统策划提给文案策划`, not like OCR-only extraction.

Always extract:
- page titles, panel titles, popup titles
- tab names, filter names, tag names, state labels
- button text, confirm text, cancel text, close hints
- tutorial prompts, unlock conditions, restriction text, warning text
- visible attribute names, field labels, module names
- result feedback text, toast-like confirmation text, empty-state text
- visible numbers when they represent a reusable format
  - examples: `{Level}`, `NO.{PetNo}`, `{CurrentExp}/{NeedExp}`, `+{DeltaValue}`, `{AttackSpeed}/秒`

Extract only the new or changed text for a state page when:
- the base page already introduced the stable title or repeated labels
- the current screenshot mainly shows a popup, overlay, expanded drawer, or state switch

Do not extract:
- designer annotations, green arrows, crop guides
- purely decorative numbers or unreadable noise
- repeated base-page text again unless the current chapter exists to review that text specifically

Before drafting rows for a page, answer these questions:
1. What player action led to this page or state?
2. What part of the UI is new relative to the previous step?
3. Which text is the player newly reading, choosing, confirming, or learning here?
4. Which numbers are literal values, and which should become format placeholders?
5. Which text needs `备注` because its purpose is not obvious from the screenshot alone?

## Required Behaviors
- Match the historical template before adding any new columns
- Separate `what is visible in the image` from `what is inferred from UX intent`
- Keep page names stable across all rows for the same screen
- Prefer conservative naming; do not invent precise text when the image is blurry
- Mark uncertain text, missing states, and cropped areas explicitly
- Prefer a single guided conversation over giving the user a list of manual setup tasks

## Output Modes

### Sample-Matched Output
Use this when the user wants content ready to paste into Feishu Excel.

Default priority:
1. same columns as the sample sheet
2. same row grouping style as the sample sheet
3. same key naming pattern as the rule doc

If the team uses the `文本键值` chapter format, prefer:
- left: screenshot or screenshot placeholder
- middle: system-planning interaction notes
- right: `key / 内容`

### Normalized Output
Use this as an internal working format when the image is complex.

Recommended fields:
- `page_name`
- `element_type`
- `element_name`
- `key`
- `content`
- `trigger_or_state`
- `source_region`
- `confidence`
- `notes`

## Page Splitting Rules
- Treat each visible screenshot-sized block as a candidate `PageNode`
- If arrows indicate progression, organize pages as `entry -> interaction -> result`
- If one base page appears with multiple overlays, split into:
  - base page
  - popup state
  - expanded panel state
  - mode-switch state
- Keep designer annotations as evidence, not as user-facing copy

## Key Naming Rules
- First obey the explicit rule doc
- If no explicit rule doc exists, infer from examples
- For the current Beagle 7-day rule doc:
  - `TAB` is the top-level module and should align with the text platform category
  - `SUBTAB` is the secondary function module and can reference the planning sheet name
  - `ID` must stay in the middle of the key, not at the tail
  - `TYPE` is the text type such as `TITLE`, `NAME`, `BUTTON`, `DESC`
  - error code or prompt texts can be exceptional, but must include a clear `备注`
- For uppercase underscore patterns, prefer forms like:
  - `LC_<SYSTEM>_<PAGE>_<ELEMENT>`
  - `LC_<SYSTEM>_<PAGE>_<STATE>_<ELEMENT>`
- Reuse the same page token inside sibling keys
- Use suffixes like `TITLE`, `DESC`, `BTN`, `TAB`, `TOAST`, `POPUP`, `INFO1` only if the sample style supports them
- Prefer semantic English tokens over numeric placeholders
  - good: `LC_PET_RESULT_SUCCESS_TITLE`
  - good: `LC_PET_RELEASE_CONFIRM_RESULT_TITLE`
  - weak: `LC_PET_RESULT_1_TITLE`
  - weak: `LC_PET_RELEASE_2_NAME`
- Use numeric IDs only when the rule doc explicitly requires a data ID in the middle token

## Beagle-Specific Rules
- Do not put `ID` at the end if the rule doc expects `TAB + SUBTAB + ID + TYPE`
- The `功能模块` field should be human-readable and should not contain the word `对话`
- Rich text placeholders should use semantic names like `{Num}` rather than generic names like `{p1}`
- If text is long or the UI is special, include `Max_Length` or mark that UI confirmation is needed

## Delivery Rules
- If the user explicitly asks for an Excel file, produce `.xlsx`, not only markdown or TSV
- Prefer screenshot-backed sections over pure text blocks when the prototype image is available
- Notes should sound like gameplay UX requirement notes, not engineering implementation notes
- If a text appears in multiple UI positions, it can be proposed once and the reuse should be stated in the note
- If the workbook is intended for review, add a `UI结构总览` section before the first screenshot chapter
- Prefer `key / 内容 / 备注` over only `key / 内容` when the user wants a planner-to-copywriter deliverable
- If a page screenshot is mismatched, partial, or clearly clipped, fix screenshot mapping first and only then refine text rows

## Validation Checklist
- [ ] Every page block has a stable page name
- [ ] Every generated key maps to one text item
- [ ] No duplicate keys unless the sample explicitly reuses them
- [ ] Unclear text is marked `待确认`
- [ ] Output structure matches the sample workbook
- [ ] Key names are semantic and readable, not mostly numeric sequence placeholders
- [ ] Each chapter screenshot matches the intended UX node or page state
- [ ] Repeated base-page text is not redundantly copied into every derived state

## Additional Resources
- Detailed workflow and data model: [reference.md](reference.md)
- Example commands and sample output: [examples.md](examples.md)
- Share and installation notes: [share-guide.md](share-guide.md)
