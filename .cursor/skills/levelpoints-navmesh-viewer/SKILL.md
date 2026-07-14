---
name: levelpoints-navmesh-viewer
description: Read Beagle Unity LevelEditor LevelPoints.json files with map navmesh JSON, generate interactive HTML previews with navmesh partitions, switchable point layers, source file replacement, browser-authorized reload controls, and area coloring from relative Beagle data paths. Use when visualizing LevelPoints on navmesh, checking whether level points are on reachable mesh, or inspecting Beagle `data/GameDatas/map_navMesh` with `UnityPrj/Assets/LevelEditorV2/Data` level point exports.
---

# LevelPoints NavMesh Viewer

Use this skill to visualize a Beagle map navmesh together with Unity LevelEditor `LevelPoints.json` placement data.

## Default Inputs

When the user does not provide paths, use:

- Navmesh: `data/GameDatas/map_navMesh/40X30_7day_MainLand_navmesh.json`
- Level points: `UnityPrj/Assets/LevelEditorV2/Data/Level_9/LevelPoints.json`
- Interactive object text table: `data/GameDatas/datas/InteractiveObj.xlsx`
- Area config table: `data/GameDatas/datas/area_config.xlsx`

If the user gives a path like `Level_9 LevelPoints.json`, first check whether the actual file is `Level_9/LevelPoints.json`.

## Bundled Scripts

Use the scripts in this skill folder:

- `scripts/analyze_levelpoints_against_navmesh.py`
- `scripts/visualize_levelpoints_navmesh.py`
- `scripts/default_point_labels.json`

For the Windows desktop build, use the Electron app under `tools/levelpoints-electron-viewer/`. It wraps the same viewer HTML in a system window. The user selects only the Beagle / project root directory; the app automatically resolves NavMesh, LevelPoints, InteractiveObj, and area_config from the default relative paths above. Refresh reloads the latest files directly by path instead of relying on browser file-picker authorization.

Prefer the system Python 3 runtime. Do not install packages unless the user asks.

## Workflow

1. Confirm the navmesh JSON has top-level `NavMeshPolygons` and each polygon has `Vertexs`.
2. Confirm the point file has top-level `components`.
3. For a one-step fresh build, run `visualize_levelpoints_navmesh.py` with `--levelpoints`, `--labels`, and `--interactive-obj-xlsx`; it will regenerate the analysis JSON/CSV before writing HTML.
4. If running the scripts separately, run `analyze_levelpoints_against_navmesh.py` first to normalize components and validate positions against the navmesh, then run `visualize_levelpoints_navmesh.py`.
5. Report the generated HTML path and summarize counts by point class, label, issue, and missing-position components.

## Output Expectations

The interactive HTML should include:

- Navmesh polygon rendering from `NavMeshPolygons[].Vertexs`.
- Base map modes: `极简模式`, `完整 NavMesh`, and `分区边界简化`. `极简模式` should keep large boundary components readable and hide boundary-side connected components whose bounding area is below `200`, including small unpaired edge fragments that appear as `outer` in raw edge matching; do not replace this with segment-length filtering.
- Coloring modes for `ProvinceID`, area category, and height `Y`. Do not include `GroupIndex`, connected component, or vertex count in the user-facing coloring dropdown. Area category must map NavMesh `ProvinceID` to `area_config.xlsx` `INT_areaID`, then use `INT_pvpType != 0` as `PVP区域`, `INT_gveType != 0` as `特殊区域`, and otherwise `普通区域`.
- Whole-view rotation (`0°`, `90°`, `180°`, `270°`) and whole-view mirror controls (`none`, horizontal, vertical, both). Default mirror should be vertical (`上下镜像`) so increasing world `Z` is displayed upward like a map view. These view transforms must apply to both NavMesh and points together and must not change raw coordinates or navmesh classification; do not rotate or mirror only one data layer unless the user explicitly asks for a diagnostic split view.
- Point layer toggles by raw type, business label, `className`, `ObjType`, `ObjID`, and `AreaID`. Do not expose an original-file-index grouping or standalone index lookup panel unless the user explicitly asks for it again.
- Point colors fixed by raw type, with prominent halo/backing/core marker rendering.
- Search by `subID`, `ObjID`, `ObjType`, `NpcID`, `TeamID`, `AreaID`, label, or prefab path.
- Hover and selected-point details showing label, class, IDs, area, layer, coordinates, matched polygon, component, prefab, and issue status.
- Source file controls that display current NavMesh and LevelPoints paths, allow changing NavMesh or LevelPoints through browser file pickers, and refresh/reload the last authorized local files with a progress bar and current reload phase. Direct path-based refresh should be handled later by an exe wrapper.
- Reload must redo the in-browser analysis steps after authorized files are read: parse NavMesh, rebuild spatial indexes, parse raw `LevelPoints.json`, normalize components, reclassify point/NavMesh matches, refresh filters, and redraw the map. It must not reuse stale embedded analysis when a newer raw `LevelPoints.json` has been authorized.
- Validation controls with a start button, progress bar, current-check text, error highlighting, and clickable error results. The default enabled check must verify whether each point is on the current NavMesh. An optional check must flag `传送车站` points placed in `PVP区域`; identify station points conservatively by `obj_display_name` containing `传送车站`, and determine PVP by the matched polygon area category from `area_config.xlsx`.
- Station distance controls with a start button, progress bar, map route rendering, and top-distance results. Identify station points by `obj_display_name` containing `传送车站`, always build the pathfinding graph from the full `NavMeshPolygons` polygon set, never from the simplified boundary or minimal base-map display, use multi-source Dijkstra to compute each station's nearest other station by approximate shortest path distance, record the polygon-center route discovered by the NavMesh graph, dedupe reciprocal nearest-neighbor routes, calculate movement time with player speed `5.8m/s`, draw only these nearest-neighbor routes as NavMesh-following polylines, and highlight the 10 longest nearest-neighbor routes with distance/time labels.

Static HTML cannot directly reread arbitrary local source paths without browser file-picker authorization. If no local file has been authorized, the refresh button should prompt the user to choose the latest `LevelPoints.json`, then immediately run the in-browser analysis flow. After the user chooses a local file, prefer the File System Access API file handle when available so refresh can call `getFile()` and read the latest disk content. Fall back to re-reading the last authorized `File` object in browsers that do not expose file handles, and make that limitation visible in the reload status. Direct path-based refresh is reserved for a future exe wrapper that can read configured disk paths as a local application.

In the Electron desktop wrapper, direct path-based refresh is allowed: the main process owns the selected root directory, resolves all source files through the fixed relative paths, reads the latest JSON from disk, and passes it to the existing page parser in NavMesh-first then LevelPoints order.

When generating HTML outside the browser, never assume an existing `artifacts/*_analysis.json` is fresh. If the raw `LevelPoints.json` may have changed, use `visualize_levelpoints_navmesh.py --levelpoints ...` or rerun `analyze_levelpoints_against_navmesh.py` first.

When reloading NavMesh, rebuild polygon and boundary spatial indexes before reclassifying points. When refreshing both NavMesh and LevelPoints, load NavMesh first, then LevelPoints, so point normalization and classification use the current base map.

Do not add point-content editing or source-file writeback unless the user explicitly asks for editing exported JSON.
