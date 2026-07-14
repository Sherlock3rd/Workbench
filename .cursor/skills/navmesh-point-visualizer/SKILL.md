---
name: navmesh-point-visualizer
description: Generate interactive HTML previews for game navmesh polygon files and level point placement exports, and validate whether points are outside the mesh or on unreachable isolated mesh components. Use when Codex is asked to visualize navmesh files, overlay monsters/NPCs/interactive objects/triggers/teams from a scenario export, or check level points against navmesh reachability for files under beagle\data\GameDatas\map_navMesh.
---

# NavMesh Point Visualizer

Use this skill to turn a navmesh JSON plus a level point/scenario JSON into an interactive HTML map and validation report.

## Required User Inputs

At the start of every use, tell the user that they need to provide both exported files:

- Mesh/navmesh JSON
- Point/scenario export JSON

The expected relative directory is:

```text
beagle\data\GameDatas\map_navMesh
```

Also tell the user the usual filename patterns:

- Mesh file: usually `地图名_navmesh.json`
- Level/scenario file: usually `Scenario_GMD_XX.json`

If the user gives only one file, ask for or infer the missing paired file only when it is safe from context.

## Bundled Scripts

Use the scripts in this skill folder:

- `scripts/analyze_gmd_points_against_navmesh.py`
- `scripts/visualize_navmesh_polygons.py`
- `scripts/export_navmesh_polygons_svg.py`

Prefer the bundled Python runtime from `load_workspace_dependencies` when available. Do not install packages; these scripts use only the standard library.

## Workflow

1. Confirm the mesh file has top-level `NavMeshPolygons` and each polygon has `Vertexs`.
2. Confirm the point file has scenario arrays such as `InteractiveObjs`, `Npcs`, `Enemies`, `SpawnTravelers`, `Teams`, and `TriggerArea`.
3. Run `analyze_gmd_points_against_navmesh.py`.
4. Run `visualize_navmesh_polygons.py` with `--points-analysis` to generate the interactive HTML overlay.
5. Optionally run `export_navmesh_polygons_svg.py` for a static preview if the user asks for an image-style artifact.
6. Report the generated HTML path and summarize the validation findings.

Example commands:

```powershell
<python> scripts/analyze_gmd_points_against_navmesh.py `
  --navmesh "<mesh-json>" `
  --scenario "<point-json>" `
  --out-json "<workspace>/points_navmesh_analysis.json" `
  --out-csv "<workspace>/points_navmesh_issues.csv"

<python> scripts/visualize_navmesh_polygons.py `
  "<mesh-json>" `
  "<workspace>/navmesh_with_points.html" `
  --points-analysis "<workspace>/points_navmesh_analysis.json"
```

## Validation Rules

When generating HTML, always also check all point data for issues. Keep these rules aligned with the previous GMD7 workflow:

- Treat the mesh plane as world `X/Z`.
- A point is valid only if its center lies inside one of the navmesh polygons.
- Build mesh reachability by connecting polygons that share an edge. The largest connected component is the main reachable mesh.
- Flag a point as `OUTSIDE_MESH` if it does not fall inside any polygon.
- Flag a point as `ISOLATED_COMPONENT` if it falls inside a polygon outside the largest connected component.
- For `Teams`, also check all child `Enemies` whose `Team` equals the team `ID`. If any child has an issue, add a `TEAM_CHILD_ISSUE` entry for the team.
- For `TriggerArea`, check the center like other points. Also sample the trigger radius circle and flag `TRIGGER_RADIUS_OUTSIDE_MESH` or `TRIGGER_RADIUS_ISOLATED_COMPONENT` if the radius extends outside the valid/main mesh.

## Output Expectations

The interactive HTML should include:

- Navmesh polygon rendering from `NavMeshPolygons[].Vertexs`.
- Coloring modes for `ProvinceID`, `GroupIndex`, height `Y`, and vertex count.
- Overlayed scenario points for interactive objects, enemies, teams, spawn points, NPCs, and triggers.
- Toggles for point layer, issue-only view, polygon strokes, and hover details.
- Hover details showing point kind, ID, AreaID, Team, Layer, coordinates, matched polygon, and issue status.

In the final response, include:

- A link to the generated HTML.
- A link to the issue CSV/JSON if issues are present or if the user asked for audit files.
- A concise summary of counts: point total, outside count, isolated count, team child issues, trigger radius issues.
