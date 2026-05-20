# Reference

## Recommended End-to-End Flow
0. Ensure the runtime environment exists.
   - On Windows, first try `py -3 --version`
   - If Python or packages are missing, run `scripts/bootstrap_env.ps1`
1. Parse the sample workbook and identify the target sheet.
2. Parse the rule doc and collect naming clues.
3. Read the prototype image with model vision.
4. Optionally pre-split the image into rough regions with `prepare_prototype_manifest.py`.
5. Build a normalized intermediate draft.
6. Transform that draft into the sample-matched Feishu Excel structure.
7. Validate duplicate keys and required columns if a row-based file was generated.

If the user wants a final production-style deliverable, add step 8:
8. Generate a screenshot-backed `.xlsx` workbook with `left screenshot + middle interaction notes + right key/content`.

## Default Assumptions
- Input prototype is a single long image or collage.
- The sample workbook is the authority for column order and grouping style.
- The explicit rule doc is the authority for `key` naming.
- When the sample workbook and the rule doc conflict, ask the user or keep both as alternatives in notes.

## Environment Bootstrap
Recommended packages:
- `openpyxl`
- `pillow`
- `python-docx`
- `rapidocr-onnxruntime`

Recommended bootstrap command on Windows:

```bash
powershell -ExecutionPolicy Bypass -File ".cursor/skills/ux-text-requirements-generator/scripts/bootstrap_env.ps1"
```

If the teammate has no Python:
1. install Python 3
2. rerun the bootstrap script
3. only skip script validation if installation is blocked

For guided teammate mode:
- the agent should do the environment check itself
- the agent should ask for install confirmation via a structured prompt
- the teammate should not be asked to copy terminal commands manually
- the teammate should only need to approve the install and provide the UX image path

## Current Beagle Rule Doc Summary
From `【Beagle】键值规范7日特供极简版.docx`, the operative rules are:
- key structure: `[TAB] + [SUBTAB] + [ID] + [TYPE]`
- translation: `[一级模块] + [次级模块] + [ID] + [文本类型]`
- `TAB` should match the existing text-platform category
- `SUBTAB` is the secondary function location and can reference the planning sheet name
- `ID` is required for pets, roles, and similar data-driven entities; for other content, use a non-repeating ID when no fixed ID exists
- `ID` must be placed in the middle, not appended at the end
- `TYPE` is the text type
- error code and prompt text can be exceptions, but `备注` is mandatory and must explain the trigger condition
- the batch entry columns are `TAB`, `KEY`, `文本`, `功能模块`, `备注`, `Max_Length`
- `功能模块` should be understandable and must not contain the word `对话`
- rich text placeholders should be semantic, such as `{Num}`, instead of generic placeholders like `{p1}`
- for long text or unusual UI, confirm max character limits with UI

## Intermediate Data Model

### `PageNode`
Represents one screen state, popup state, or mode state.

```json
{
  "page_name": "Map_AreaPanel",
  "page_type": "page",
  "parent_page": "Map_Main",
  "state_tag": "area_panel_expanded",
  "source_region": "region_04",
  "notes": "Right-side area list expanded from map page."
}
```

### `TextElement`
Represents one visible or inferred text requirement item.

```json
{
  "page_name": "Map_AreaPanel",
  "element_type": "button",
  "element_name": "area_tab",
  "visible_text": "AREA",
  "suggested_key": "LC_MAP_AREA_PANEL_TAB_TITLE",
  "trigger_or_state": "panel expanded",
  "confidence": "high"
}
```

### `RequirementRow`
Represents one final Excel-compatible row.

```json
{
  "页面名": "地图区域面板",
  "key": "LC_MAP_AREA_PANEL_TAB_TITLE",
  "内容": "AREA",
  "备注": "右侧展开面板标题"
}
```

### `WorkbookSection`
Represents one chapter in the final section-based Excel deliverable.

```json
{
  "title": "宠物进化预览页",
  "crop_box": [574, 57, 853, 302],
  "image_note": "【左侧放图】原型右上进化流程图：玩家查看进化前后形态和条件的预览页。",
  "rows": [
    {
      "note": "玩家点击进化入口后，进入宠物进化预览页，用于查看进化前后形态对比。",
      "key": "LC_PET_EVOLUTION_1_TITLE",
      "content": "待确认"
    }
  ]
}
```

## Sample-Matched Output
If the sample workbook is section-based rather than flat-column-based, follow this shape:

1. Page title line
2. Optional design notes or behavior notes
3. `key / 内容` header row
4. One row per text element

This repo's current sample workbook contains a sheet named `文本键值`, which behaves like a section-based template:
- page title appears as a standalone line
- `key` and `内容` appear as the core columns
- one page can contain many requirement rows below the same title

Use that as the fallback output style when no richer schema is found.

## Final Excel Layout
When the user asks for a directly usable workbook, prefer this layout:
- top section: `UI结构总览`
- columns `A-E`: screenshot area
- columns `G-I`: interaction notes written from the system-design perspective
- columns `K-Q`: `key / 内容 / 备注`

This mirrors the team's current review habit:
- first explain the whole feature structure and reading order
- left side explains where the copy is used
- right side lists what text needs copywriting support and why it exists

Recommended overview rows:
- module
- page list
- reading notes

## Page Naming Heuristics
- Use `模块_页面_状态` or the team's existing page naming pattern.
- If the image contains the same base map with different overlays, keep the base page token stable.
- Good:
  - `Map_Main`
  - `Map_TrackingPopup`
  - `Map_AreaPanel`
  - `Map_ModeSwitchMenu`
- Avoid:
  - naming pages only by coordinates
  - using visual colors as the main page identifier
  - merging popup text into the base page if the popup changes interaction state

## Text Element Categories
- `title`
- `subtitle`
- `button_primary`
- `button_secondary`
- `tab`
- `popup_title`
- `popup_body`
- `tooltip`
- `toast`
- `label`
- `empty_state`
- `error_state`
- `system_annotation`

Do not convert `system_annotation` into player-facing copy unless the rule doc or prototype explicitly says it is on-screen text.

## Text Requirement Extraction Heuristics
Use this sequence for each page:

1. Identify the UX role of the page:
   - entry page
   - detail page
   - popup
   - tooltip
   - drawer
   - confirmation state
   - result state
2. Identify what changed from the previous visible state.
3. Extract all user-facing text in the changed area first.
4. Add stable page-level text only if this page is the first chapter where that text matters.
5. Convert raw numbers to placeholders when the number is obviously variable.

Usually include:
- titles and section headers
- button text
- tab and filter labels
- attribute names
- tags and rarity labels
- unlock conditions
- warning and confirmation copy
- progress and value formats

Usually exclude:
- green arrows and planning notes
- duplicated text already captured in the previous base state
- unreadable fragments that cannot be responsibly inferred

For numbers, prefer format-style content:
- `90` -> `{Level}` when it is a level badge
- `2/秒` -> `{AttackSpeed}/秒` when it is a display pattern
- `1,380/6,420` -> `{CurrentExp}/{NeedExp}` when it is a resource progress format

For repeated states, ask:
- Is this text newly introduced?
- Is this text meaningfully changed?
- Is this text in a newly opened panel or popup?
- Does copywriting need to review it separately even if repeated?

If the answer is no to all four, do not add another row just because the text is still visible.

## Key Naming Heuristics
- Prefer explicit prefixes from the rule doc.
- If examples show localization keys like `LC_KINGDOMWAR_ALLIANCESIGN_RULE_1`, infer:
  - uppercase snake case
  - stable system prefix
  - page/group token in the middle
  - element/function suffix at the end
- When generating new keys, prefer semantic tokens over coordinates and over sequence numbers:
  - good: `LC_MAP_TRACKING_POPUP_CANCEL_BTN`
  - good: `LC_PET_RESULT_SUCCESS_TITLE`
  - weak: `LC_MAP_POPUP_1_BTN`
  - weak: `LC_PET_RESULT_1_TITLE`

When the Beagle rule doc is in force, convert the above heuristic into this stronger template:
- `LC_<TAB>_<SUBTAB>_<ID>_<TYPE>`
- if the asset is data-driven, prefer the real config ID
- if the asset is page text, use a stable, non-repeating middle ID rather than moving the ID to the suffix

Examples from the rule doc:
- `LC_FTE_CHOICE_1_TITLE`
- `LC_FTE_CHOICE_1001_NAME`
- `LC_PET_INFO_80001_NAME`
- `LC_SKILL_INFO_90001_DESC`

For new UI chapter text that is not data-ID driven, prefer semantic forms like:
- `LC_PET_RELEASE_CONFIRM_RESULT_TITLE`
- `LC_PET_SKILL_OVERVIEW_STAR_UNLOCK_TIP`
- `LC_PET_DETAIL_BASE_UPGRADE_BUTTON`

Avoid:
- adding `1`, `2`, `3` only to distinguish rows
- using `INFO1`, `INFO2`, `LABEL1` unless the UI really has repeated sibling items with no better semantic distinction

## Confidence Rules
- `high`: text is clearly readable or directly specified
- `medium`: structure is clear but some wording is inferred
- `low`: blurry text or partially cropped area

If confidence is `low`, add `待确认` to notes or output.

## Prototype Annotation Rules
- Green and red notes in a stitched image are usually designer annotations.
- Keep them as implementation hints, not user-visible content.
- Arrows usually imply transitions and should influence page grouping.
- If timestamps or resolution labels appear on the canvas border, ignore them.
- If one screenshot block contains a base page plus a popup overlay, decide whether it is:
  - one UX node with overlay evidence
  - or two true review chapters
- Prefer one chapter when the popup is clearly part of the same final screenshot state and the user wants chapter readability over micro-splitting

## Screenshot Mapping Recovery
If screenshots in the workbook do not match the intended chapters, debug in this order:
1. Check whether the section should use the main stitched image or an original local crop asset.
2. Check whether `source_coordinate_size` matches the coordinate system used when the crop box was defined.
3. Check whether one UX node was accidentally split into multiple sections.
4. Check whether a tiny crop box is only capturing a title strip or local corner.
5. Rebuild the workbook and inspect the generated crop images before trusting the Excel.

## Writing Notes For Copywriters
Use a gameplay UX requirement tone.

Good:
- `玩家点击地图目标后，弹出追踪确认窗，用于二次确认本次地图追踪操作。`
- `玩家进入宠物详情主页后，页面顶部显示宠物名称，用于明确当前查看的宠物对象。`

Avoid:
- `点击按钮触发弹窗`
- `接口返回后刷新文案`
- `这里有个标题`

## Suggested Script Usage

### 1. Inspect workbook schema
```bash
py -3 ".cursor/skills/ux-text-requirements-generator/scripts/extract_sheet_schema.py" "文本需求案例.xlsx" --sheet "文本键值"
```

### 2. Extract key hints
```bash
py -3 ".cursor/skills/ux-text-requirements-generator/scripts/extract_rule_hints.py" "【Beagle】键值规范7日特供极简版.docx" "文本需求案例.xlsx"
```

### 3. Build prototype manifest
```bash
py -3 ".cursor/skills/ux-text-requirements-generator/scripts/prepare_prototype_manifest.py" "prototype.png" --ocr none
```

### 4. Validate row output
```bash
py -3 ".cursor/skills/ux-text-requirements-generator/scripts/validate_requirement_rows.py" "draft.json" --required-columns "页面名,key,内容"
```

### 5. Generate final workbook from config
```bash
py -3 "tools/build_ux_requirement_workbook.py" "tools/pet_growth_requirement_config.json"
```

### 6. Share-ready output
Keep these files ready if the skill will be shared with teammates:
- `.cursor/skills/ux-text-requirements-generator/SKILL.md`
- `.cursor/skills/ux-text-requirements-generator/reference.md`
- `.cursor/skills/ux-text-requirements-generator/examples.md`
- `.cursor/skills/ux-text-requirements-generator/share-guide.md`
- `.cursor/skills/ux-text-requirements-generator/workbook_config_template.json`
- `tools/build_ux_requirement_workbook.py`

## Output Recommendation Under The Beagle Rule
If the user wants direct Feishu Excel paste-ready content, prefer a row structure that can map to:
- `TAB`
- `KEY`
- `文本`
- `功能模块`
- `备注`
- `Max_Length`

If the historical sample still uses a section-based `key / 内容` layout, keep two layers:
1. normalized draft with the six Beagle columns
2. sample-matched display block for review

This avoids losing rule-doc-required fields while still staying close to the team's current sheet style.

## Failure Recovery
- If the sample workbook cannot be parsed, fall back to a normalized JSON draft and tell the user what was missing.
- If the prototype image is too dense, split it into page candidates first, then write requirements page by page.
- If OCR is unavailable, rely on model vision for text extraction and mark uncertain text.
- If key rules are incomplete, generate a proposed key plus a `待确认` note rather than pretending certainty.
- If a screenshot-backed workbook layout overlaps, separate image area, note area, and key/content area into distinct column groups before adjusting text.
- If teammates did not provide a sample workbook or rule doc, use the built-in template and Beagle rule summary from this skill, and label the result as `默认规则推导版`.
