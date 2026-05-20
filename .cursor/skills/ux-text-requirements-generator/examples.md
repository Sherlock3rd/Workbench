# Examples

## Example 1: Standard User Request
User request:

```text
请根据这张 UX 长图，按 @文本需求案例.xlsx 的格式输出文本需求。
key 规则参考 @【Beagle】键值规范7日特供极简版.docx，不确定的地方标记待确认。
```

Recommended agent flow:
0. Prepare Python if needed with `bootstrap_env.ps1`
1. Run `extract_sheet_schema.py` on the sample workbook.
2. Run `extract_rule_hints.py` on the rule doc and the sample workbook.
3. Read the UX image with model vision.
4. Optionally run `prepare_prototype_manifest.py`.
5. Draft a normalized page list.
6. Convert it into the sample workbook's structure.

Recommended command:

```bash
py -3 ".cursor/skills/ux-text-requirements-generator/scripts/extract_rule_hints.py" "C:\\Users\\wangpeng\\Downloads\\【Beagle】键值规范7日特供极简版.docx" "文本需求案例.xlsx"
```

## Example 2: Guided Teammate Request
User request:

```text
请用 ux-text-requirements-generator 处理这张图：
D:\demo\pet_flow.png
```

Recommended agent flow:
1. Confirm the UX image path.
2. Ask whether missing dependencies may be installed automatically.
3. Check Python and dependencies yourself.
4. If sample workbook or rule doc is not provided, search the workspace for likely defaults.
5. If no defaults are found, continue with the built-in workbook template and Beagle rule summary.
6. Split chapters, draft rows, build workbook, and return the output path.

The teammate should only need to provide the image path and approve prompts.

## Example 3: Current Repo Sample Pattern
The current sample workbook contains a `文本键值` sheet whose practical structure is:
- standalone page section title
- optional design/behavior note rows
- `key`
- `内容`

That means a valid output can be grouped like this:

```text
地图主页面
1. 点击追踪按钮后，弹出追踪确认弹窗。
key    内容
LC_MAP_TRACKING_POPUP_TITLE    追踪目标
LC_MAP_TRACKING_POPUP_CANCEL_BTN    取消追踪
LC_MAP_TRACKING_POPUP_CONFIRM_BTN    开始追踪
```

## Example 4: Normalized Draft For A Map Prototype
For a stitched map prototype with one base page and several overlays, a good intermediate draft looks like:

```json
[
  {
    "page_name": "Map_Main",
    "element_type": "label",
    "element_name": "mode_label",
    "key": "LC_MAP_MODE_COMMON_LABEL",
    "content": "Common mode",
    "trigger_or_state": "default state",
    "source_region": "region_01",
    "confidence": "high",
    "notes": ""
  },
  {
    "page_name": "Map_TrackingPopup",
    "element_type": "popup_title",
    "element_name": "tracking_title",
    "key": "LC_MAP_TRACKING_POPUP_TITLE",
    "content": "MARK LINE",
    "trigger_or_state": "tracking popup open",
    "source_region": "region_02",
    "confidence": "medium",
    "notes": "Popup copy should be checked against the source image."
  },
  {
    "page_name": "Map_AreaPanel",
    "element_type": "title",
    "element_name": "area_panel_title",
    "key": "LC_MAP_AREA_PANEL_TITLE",
    "content": "AREA",
    "trigger_or_state": "area list expanded",
    "source_region": "region_03",
    "confidence": "high",
    "notes": ""
  }
]
```

## Example 5: Validation Command
```bash
py -3 ".cursor/skills/ux-text-requirements-generator/scripts/validate_requirement_rows.py" ".cursor/skills/ux-text-requirements-generator/sample_map_requirements.json" --required-columns "page_name,key,content" --key-regex "^[A-Z0-9]+(?:_[A-Z0-9]+)+$"
```

## Example 6: Beagle Rule-Matched Row Draft
If the final deliverable needs to follow the Beagle batch-entry fields, a row should look like:

```json
{
  "TAB": "MAP",
  "KEY": "LC_MAP_AREA_PANEL_TITLE",
  "文本": "AREA",
  "功能模块": "地图区域面板",
  "备注": "右侧区域列表展开时显示的面板标题",
  "Max_Length": ""
}
```

## Example 7: Final Screenshot-Backed Excel
When the user asks for a final workbook instead of plain text:

1. Create a config JSON describing:
   - source image
   - output workbook path
   - section titles
   - crop boxes
   - screenshot notes
   - interaction notes
   - `key / 内容`
2. Run the workbook builder:

```bash
py -3 "tools/build_ux_requirement_workbook.py" "tools/pet_growth_requirement_config.json"
```

Expected result:
- one `.xlsx` workbook
- a UI structure overview at the top
- each section has a screenshot on the left
- interaction notes in the middle
- `key / 内容 / 备注` on the right
- note style matches `系统策划提给文案策划`

## Example 8: First-Time Setup On A New Machine
If the teammate has not installed Python packages yet:

```powershell
powershell -ExecutionPolicy Bypass -File ".cursor/skills/ux-text-requirements-generator/scripts/bootstrap_env.ps1"
```

Then verify:

```powershell
py -3 ".cursor/skills/ux-text-requirements-generator/scripts/extract_sheet_schema.py" "文本需求案例.xlsx" --sheet "文本键值"
```

## Example 9: Semantic Key Naming
Use semantic English tokens instead of sequence numbers when the text item has a clear meaning:

```json
[
  {
    "key": "LC_PET_RESULT_SUCCESS_TITLE",
    "content": "升级成功"
  },
  {
    "key": "LC_PET_RESULT_SUCCESS_DESC",
    "content": "飞起来俯冲攻击，对沿途敌人造成伤害。"
  },
  {
    "key": "LC_PET_RELEASE_CONFIRM_RESULT_TITLE",
    "content": "RELEASE RESULT"
  }
]
```

Avoid:

```json
[
  { "key": "LC_PET_RESULT_1_TITLE" },
  { "key": "LC_PET_RESULT_2_DESC" },
  { "key": "LC_PET_RELEASE_CONFIRM_3_RESULT" }
]
```

## Example 10: Which Text Should Be Added For A State Page
State change:
- base page already has pet name, page title, and bottom main buttons
- new screenshot only adds an attribute detail drawer on the right

Good output:
- drawer title
- attribute names shown only inside the drawer
- value format rows used by the drawer
- a note explaining that the drawer is opened from the detail page

Weak output:
- copy the whole base page title set again
- duplicate the same pet name row unless this chapter reviews naming specifically

## Example 11: Share Skill With Teammates
If the user wants to share the skill with others inside the same repo:

1. Keep the project skill under `.cursor/skills/ux-text-requirements-generator/`
2. Keep `tools/build_ux_requirement_workbook.py` in the repo
3. Provide a starter config template, `requirements.txt`, and a bootstrap script
4. If needed, include one polished example workbook config such as `tools/pet_growth_requirement_config_v12.json`

For prompt or error text:

```json
{
  "TAB": "ERROR",
  "KEY": "LC_ERROR_3508",
  "文本": "目标选择错误",
  "功能模块": "地图追踪",
  "备注": "对不正确的目标释放时触发",
  "Max_Length": ""
}
```
