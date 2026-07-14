# LevelPoints HTML Editor Writeback Reference

## Editor UI Requirements

The HTML editor should add editing on top of the existing viewer, not replace the viewer:

- Select a point from search, hover, validation result, or map click.
- Show original values and edited values side by side.
- Support position editing by direct numeric input first; drag editing can be added later.
- Mark dirty points clearly on the map and in filters.
- Provide undo for the selected point and reset-all for the current session.
- Export patch JSON and a human-readable change summary.

Do not add direct source overwrite in static HTML unless the user has explicitly accepted browser file permission limitations.

## Editable Fields

Default editable fields:

- `position.x`
- `position.y`
- `position.z`
- `serializedData.MonoBehaviour.ObjID`
- `serializedData.MonoBehaviour.ObjType`
- `serializedData.MonoBehaviour.AreaID`
- `serializedData.MonoBehaviour.NpcID`
- `serializedData.MonoBehaviour.TeamID`
- `serializedData.MonoBehaviour.BelongToLayerID`
- `serializedData.MonoBehaviour.SubID`

Any other Unity field must be confirmed before adding it to the editor or passing it through `--allow-field`.

## Patch Schema

Patch files use:

```json
{
  "format": "levelpoints-html-editor-patch/v1",
  "source": {
    "levelpoints": "UnityPrj/Assets/LevelEditorV2/Data/Level_9/LevelPoints.json"
  },
  "edits": []
}
```

Each edit:

```json
{
  "index": 123,
  "match": {
    "subID": 456,
    "className": "LevelPointInteractiveObj",
    "prefabPath": "Assets/..."
  },
  "position": {
    "x": 100.0,
    "y": 0.0,
    "z": 200.0
  },
  "monoBehaviour": {
    "ObjID": 1001
  },
  "note": "optional editor note"
}
```

Rules:

- `index` is required and points to `components[index]`.
- `match` is optional but strongly recommended. The writeback script rejects the edit if the current source does not match.
- Omit unchanged fields; do not repeat the whole component.
- Keep numeric fields as JSON numbers, not strings.

## Safe Writeback Flow

1. Export `artifacts/levelpoints_editor_patch.json` from the HTML editor.
2. Apply it to the original `LevelPoints.json` and write a new output file.
3. Re-run `levelpoints-navmesh-viewer` analysis against the new output.
4. Compare the old and new summaries before telling Unity to consume the file.

Example:

```powershell
py -3 .cursor/skills/levelpoints-html-editor-writeback/scripts/apply_levelpoints_patch.py `
  --levelpoints "UnityPrj/Assets/LevelEditorV2/Data/Level_9/LevelPoints.json" `
  --patch "artifacts/levelpoints_editor_patch.json" `
  --out "artifacts/LevelPoints.edited.json" `
  --summary "artifacts/levelpoints_editor_writeback_summary.json"

py -3 .cursor/skills/levelpoints-navmesh-viewer/scripts/analyze_levelpoints_against_navmesh.py `
  --navmesh "data/GameDatas/map_navMesh/40X30_7day_MainLand_navmesh.json" `
  --levelpoints "artifacts/LevelPoints.edited.json" `
  --labels ".cursor/skills/levelpoints-navmesh-viewer/scripts/default_point_labels.json" `
  --interactive-obj-xlsx "data/GameDatas/datas/InteractiveObj.xlsx" `
  --out-json "artifacts/levelpoints_edited_analysis.json" `
  --out-csv "artifacts/levelpoints_edited_issues.csv"
```

## Unity Consumption

Unity can read the generated JSON as long as:

- The top-level structure is still the original `LevelPoints.json` structure.
- `components` remains an array.
- Existing component objects are patched in place instead of replaced with flattened analysis records.
- Encoding is UTF-8 JSON.

If the user wants Unity to read the file from the original project path, ask before overwriting and recommend keeping a timestamped backup.
