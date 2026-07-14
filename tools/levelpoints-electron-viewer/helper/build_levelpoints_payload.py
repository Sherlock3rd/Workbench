#!/usr/bin/env python3
import argparse
import csv
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_analysis(analyzer, navmesh_path, levelpoints_path, labels_path, interactive_obj_xlsx, out_json, out_csv):
    nav = json.loads(Path(navmesh_path).read_text(encoding="utf-8-sig"))
    levelpoints = json.loads(Path(levelpoints_path).read_text(encoding="utf-8-sig"))
    labels = analyzer.load_labels(labels_path)
    interactive_names = analyzer.load_interactive_obj_names(interactive_obj_xlsx)
    polys = analyzer.build_navmesh(nav)
    comp, comp_sizes = analyzer.components(polys)
    main_comp = max(range(len(comp_sizes)), key=lambda i: comp_sizes[i]) if comp_sizes else None
    index = analyzer.build_spatial_index(polys)

    points = []
    skipped = []
    for i, component in enumerate(levelpoints.get("components", [])):
        point = analyzer.normalize_point(component, i, labels, interactive_names)
        if point is None:
            skipped.append({"index": i, "class_name": component.get("className"), "reason": "NO_POSITION"})
            continue
        point["nav"] = analyzer.classify_point(point, polys, index, comp, main_comp)
        points.append(point)

    issues = []
    for point in points:
        if point["nav"].get("issue"):
            issues.append({
                "index": point["index"],
                "issue": point["nav"]["issue"],
                "label": point["label"],
                "class_name": point["class_name"],
                "sub_id": point["sub_id"],
                "obj_id": point["obj_id"],
                "obj_display_name": point["obj_display_name"],
                "obj_type": point["obj_type"],
                "npc_id": point["npc_id"],
                "team_id": point["team_id"],
                "area_id": point["area_id"],
                "x": point["x"],
                "y": point["y"],
                "z": point["z"],
                "component": point["nav"]["component"],
                "poly": point["nav"]["poly"],
                "prefab_path": point["prefab_path"],
            })

    summary = {
        "navmesh": str(navmesh_path),
        "levelpoints": str(levelpoints_path),
        "label_config": str(labels_path) if labels_path else None,
        "interactive_obj_xlsx": str(interactive_obj_xlsx) if interactive_obj_xlsx else None,
        "level_id": levelpoints.get("levelId"),
        "level_version": levelpoints.get("version"),
        "polygon_count": len(polys),
        "component_count": len(comp_sizes),
        "main_component": main_comp,
        "main_component_size": comp_sizes[main_comp] if main_comp is not None else 0,
        "raw_component_count": len(levelpoints.get("components", [])),
        "point_count": len(points),
        "skipped_component_count": len(skipped),
        "class_counts": Counter(p["class_name"] for p in points),
        "label_counts": Counter(p["label"] for p in points),
        "inside_count": sum(1 for p in points if p["nav"]["inside"]),
        "outside_count": sum(1 for p in points if not p["nav"]["inside"]),
        "isolated_count": sum(1 for p in points if p["nav"]["issue"] == "ISOLATED_COMPONENT"),
        "issue_counts": Counter(i["issue"] for i in issues),
    }

    out_json = Path(out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(
        json.dumps({"summary": summary, "issues": issues, "points": points, "skipped": skipped}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    out_csv = Path(out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fields = ["index", "issue", "label", "class_name", "sub_id", "obj_id", "obj_display_name", "obj_type", "npc_id", "team_id", "area_id", "x", "y", "z", "component", "poly", "prefab_path"]
    with out_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(issues)


def render_html(visualizer, navmesh, analysis, output, area_config):
    old_argv = sys.argv[:]
    try:
        sys.argv = [
            "visualize_levelpoints_navmesh.py",
            str(navmesh),
            str(analysis),
            str(output),
            "--area-config",
            str(area_config),
        ]
        visualizer.main()
    finally:
        sys.argv = old_argv


def main():
    parser = argparse.ArgumentParser(description="Build LevelPoints viewer HTML for Electron.")
    parser.add_argument("--scripts-dir", required=True)
    parser.add_argument("--navmesh", required=True)
    parser.add_argument("--levelpoints", required=True)
    parser.add_argument("--labels", required=True)
    parser.add_argument("--interactive-obj-xlsx", required=True)
    parser.add_argument("--area-config", required=True)
    parser.add_argument("--analysis", required=True)
    parser.add_argument("--issues-csv", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    scripts_dir = Path(args.scripts_dir)
    analyzer = load_module("levelpoints_analyzer", scripts_dir / "analyze_levelpoints_against_navmesh.py")
    visualizer = load_module("levelpoints_visualizer", scripts_dir / "visualize_levelpoints_navmesh.py")

    build_analysis(
        analyzer,
        args.navmesh,
        args.levelpoints,
        args.labels,
        args.interactive_obj_xlsx,
        args.analysis,
        args.issues_csv,
    )
    render_html(visualizer, args.navmesh, args.analysis, args.output, args.area_config)
    print(json.dumps({"output": args.output, "analysis": args.analysis, "issuesCsv": args.issues_csv}, ensure_ascii=False))


if __name__ == "__main__":
    main()
