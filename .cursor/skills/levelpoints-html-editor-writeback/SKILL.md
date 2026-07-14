---
name: levelpoints-html-editor-writeback
description: Add HTML editing and safe writeback for Beagle Unity LevelEditor LevelPoints.json data. Use when the user asks to edit LevelPoints in an HTML navmesh viewer, export modified point data, write changes back from HTML to JSON, or produce Unity-readable edited level point files.
---

# LevelPoints HTML Editor Writeback

Use this skill when the task is no longer read-only visualization and explicitly requires editing LevelPoints data in HTML, exporting edits, or producing a JSON file that Unity can read.

## Boundary

- Keep this separate from `levelpoints-navmesh-viewer`, which remains the read-only preview and validation workflow.
- Do not silently overwrite the original `LevelPoints.json`. Default to writing a new file such as `artifacts/LevelPoints.edited.json`.
- The browser editor should export a patch JSON. A local script applies that patch to the source `LevelPoints.json`.
- Browser-only static HTML cannot directly write arbitrary local files. Use download, File System Access API with user permission, or a local wrapper for direct save.

## Default Inputs

Use the same defaults as `levelpoints-navmesh-viewer` unless the user provides paths:

- Navmesh: `data/GameDatas/map_navMesh/40X30_7day_MainLand_navmesh.json`
- Level points: `UnityPrj/Assets/LevelEditorV2/Data/Level_9/LevelPoints.json`
- Existing viewer HTML: `artifacts/levelpoints_navmesh.html`

## Writeback Contract

The HTML editor must export this patch format:

```json
{
  "format": "levelpoints-html-editor-patch/v1",
  "edits": [
    {
      "index": 123,
      "match": {
        "subID": "optional stable identity",
        "className": "optional class guard",
        "prefabPath": "optional prefab guard"
      },
      "position": {
        "x": 1.0,
        "y": 0.0,
        "z": 2.0
      },
      "monoBehaviour": {
        "ObjID": 1001,
        "ObjType": 1,
        "AreaID": 9
      }
    }
  ]
}
```

Use `components[]` `index` as the writeback anchor, and include `match` guards whenever possible to avoid applying edits to a stale or reordered file.

## Bundled Script

Use `scripts/apply_levelpoints_patch.py` to produce the Unity-readable JSON:

```powershell
py -3 .cursor/skills/levelpoints-html-editor-writeback/scripts/apply_levelpoints_patch.py `
  --levelpoints "UnityPrj/Assets/LevelEditorV2/Data/Level_9/LevelPoints.json" `
  --patch "artifacts/levelpoints_editor_patch.json" `
  --out "artifacts/LevelPoints.edited.json" `
  --summary "artifacts/levelpoints_editor_writeback_summary.json"
```

The script updates:

- `components[index].position.x/y/z`
- whitelisted `components[index].serializedData.MonoBehaviour` fields: `ObjID`, `ObjType`, `AreaID`, `NpcID`, `TeamID`, `BelongToLayerID`, `SubID`

Use `--allow-field FieldName` only when the user has confirmed the target Unity field name.

## Workflow

1. Read `rules/rules.md` and relevant `mistakes/navmesh-*.md` before changing editor or writeback behavior.
2. Start from a fresh viewer build; do not rely on stale `artifacts/levelpoints_navmesh_analysis.json`.
3. Add or update HTML editor UI only after confirming the editable fields.
4. Export edits as `levelpoints-html-editor-patch/v1`.
5. Apply the patch with `apply_levelpoints_patch.py` to a new JSON file.
6. Re-run the navmesh analysis on the edited JSON and compare changed counts and validation issues.
7. Tell the user which output file Unity should read.

## Validation

After writeback, verify:

- Patch applies without identity mismatch.
- Changed indices match the user-edited points.
- Edited file still has top-level `components`.
- Re-analysis uses the edited JSON, not the old analysis artifact.
- No new outside-navmesh or isolated-component issues were introduced unless expected.

See [reference.md](reference.md) for editor UI requirements and the patch schema details.
