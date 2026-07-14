#!/usr/bin/env python3
import argparse
import csv
import json
import math
from collections import Counter, defaultdict, deque
from pathlib import Path


POINT_KINDS = ["InteractiveObjs", "Npcs", "Enemies", "SpawnTravelers", "Teams", "TriggerArea"]


def pos_of(obj):
    pos = obj.get("Pos")
    if not isinstance(pos, dict):
        return None
    return float(pos.get("x", 0)), float(pos.get("y", 0)), float(pos.get("z", 0))


def polygon_vertices(poly):
    return [(float(v.get("x", 0)), float(v.get("z", 0))) for v in poly.get("Vertexs") or []]


def point_in_poly(x, z, verts):
    inside = False
    n = len(verts)
    for i in range(n):
        x1, z1 = verts[i]
        x2, z2 = verts[(i + 1) % n]
        # Boundary counts as inside.
        dx, dz = x2 - x1, z2 - z1
        cross = (x - x1) * dz - (z - z1) * dx
        if abs(cross) < 1e-5 and min(x1, x2) - 1e-5 <= x <= max(x1, x2) + 1e-5 and min(z1, z2) - 1e-5 <= z <= max(z1, z2) + 1e-5:
            return True
        if ((z1 > z) != (z2 > z)):
            x_at_z = (x2 - x1) * (z - z1) / (z2 - z1 + 1e-12) + x1
            if x < x_at_z:
                inside = not inside
    return inside


def dist_point_segment(px, pz, ax, az, bx, bz):
    dx, dz = bx - ax, bz - az
    length2 = dx * dx + dz * dz
    if length2 == 0:
        return math.hypot(px - ax, pz - az)
    t = max(0, min(1, ((px - ax) * dx + (pz - az) * dz) / length2))
    x = ax + t * dx
    z = az + t * dz
    return math.hypot(px - x, pz - z)


def dist_to_poly(x, z, verts):
    if not verts:
        return None
    return min(dist_point_segment(x, z, *verts[i], *verts[(i + 1) % len(verts)]) for i in range(len(verts)))


def build_spatial_index(polys, cell_size=20.0):
    index = defaultdict(list)
    for i, poly in enumerate(polys):
        xs = [v[0] for v in poly["verts"]]
        zs = [v[1] for v in poly["verts"]]
        poly["bbox"] = (min(xs), min(zs), max(xs), max(zs))
        min_cx = int(math.floor(poly["bbox"][0] / cell_size))
        max_cx = int(math.floor(poly["bbox"][2] / cell_size))
        min_cz = int(math.floor(poly["bbox"][1] / cell_size))
        max_cz = int(math.floor(poly["bbox"][3] / cell_size))
        for cx in range(min_cx, max_cx + 1):
            for cz in range(min_cz, max_cz + 1):
                index[(cx, cz)].append(i)
    return index


def candidate_polys(index, x, z, cell_size=20.0):
    cx = int(math.floor(x / cell_size))
    cz = int(math.floor(z / cell_size))
    seen = set()
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            for i in index.get((cx + dx, cz + dz), []):
                if i not in seen:
                    seen.add(i)
                    yield i


def components(polys):
    edge_to_polys = defaultdict(list)
    for i, poly in enumerate(polys):
        verts = poly["verts"]
        for a, b in zip(verts, verts[1:] + verts[:1]):
            key = tuple(sorted(((round(a[0], 3), round(a[1], 3)), (round(b[0], 3), round(b[1], 3)))))
            edge_to_polys[key].append(i)

    graph = [[] for _ in polys]
    for members in edge_to_polys.values():
        if len(members) < 2:
            continue
        for i in members:
            graph[i].extend(j for j in members if j != i)

    comp = [-1] * len(polys)
    sizes = []
    for start in range(len(polys)):
        if comp[start] != -1:
            continue
        cid = len(sizes)
        q = deque([start])
        comp[start] = cid
        count = 0
        while q:
            cur = q.popleft()
            count += 1
            for nxt in graph[cur]:
                if comp[nxt] == -1:
                    comp[nxt] = cid
                    q.append(nxt)
        sizes.append(count)
    return comp, sizes


def nearest_poly(x, z, polys, index):
    best = None
    best_d = float("inf")
    # Expand a few rings so out-of-mesh diagnostics are useful.
    cx = int(math.floor(x / 20.0))
    cz = int(math.floor(z / 20.0))
    seen = set()
    for ring in range(0, 6):
        for ix in range(cx - ring, cx + ring + 1):
            for iz in range(cz - ring, cz + ring + 1):
                if abs(ix - cx) != ring and abs(iz - cz) != ring:
                    continue
                for pi in index.get((ix, iz), []):
                    if pi in seen:
                        continue
                    seen.add(pi)
                    d = dist_to_poly(x, z, polys[pi]["verts"])
                    if d is not None and d < best_d:
                        best = pi
                        best_d = d
        if best is not None and best_d < ring * 20:
            break
    return best, best_d if best is not None else None


def classify_point(point, polys, index, comp, main_comp):
    x, _, z = point["pos"]
    found = None
    for pi in candidate_polys(index, x, z):
        bx1, bz1, bx2, bz2 = polys[pi]["bbox"]
        if x < bx1 - 1e-6 or x > bx2 + 1e-6 or z < bz1 - 1e-6 or z > bz2 + 1e-6:
            continue
        if point_in_poly(x, z, polys[pi]["verts"]):
            found = pi
            break
    if found is None:
        near, dist = nearest_poly(x, z, polys, index)
        return {
            "inside": False,
            "poly": None,
            "component": None,
            "main": False,
            "nearest_poly": near,
            "nearest_distance": dist,
            "issue": "OUTSIDE_MESH",
        }
    cid = comp[found]
    return {
        "inside": True,
        "poly": found,
        "component": cid,
        "main": cid == main_comp,
        "nearest_poly": found,
        "nearest_distance": 0.0,
        "issue": None if cid == main_comp else "ISOLATED_COMPONENT",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--navmesh", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-csv", required=True)
    args = parser.parse_args()

    nav = json.loads(Path(args.navmesh).read_text(encoding="utf-8-sig"))
    scenario = json.loads(Path(args.scenario).read_text(encoding="utf-8-sig"))

    polys = []
    for i, poly in enumerate(nav.get("NavMeshPolygons", [])):
        verts = polygon_vertices(poly)
        if len(verts) >= 3:
            polys.append({
                "source_index": i,
                "polygon_index": poly.get("PolygonIndex", i),
                "province": poly.get("ProvinceID"),
                "group": poly.get("GroupIndex"),
                "verts": verts,
            })

    comp, comp_sizes = components(polys)
    main_comp = max(range(len(comp_sizes)), key=lambda i: comp_sizes[i])
    index = build_spatial_index(polys)

    points = []
    for kind in POINT_KINDS:
        for obj in scenario.get(kind, []):
            pos = pos_of(obj)
            if not pos:
                continue
            points.append({
                "kind": kind,
                "id": obj.get("ID"),
                "obj_id": obj.get("ObjID") or obj.get("NpcID") or obj.get("PetMonsterID") or obj.get("CfgID") or obj.get("TeamID"),
                "team": obj.get("Team"),
                "area_id": obj.get("AreaID"),
                "layer": obj.get("Layer"),
                "radius": obj.get("Radius"),
                "pos": pos,
                "raw": obj,
            })

    by_id = {(p["kind"], p["id"]): p for p in points}
    children_by_team = defaultdict(list)
    for p in points:
        if p["kind"] == "Enemies" and p.get("team") not in (None, 0):
            children_by_team[p["team"]].append(p)

    for p in points:
        p["nav"] = classify_point(p, polys, index, comp, main_comp)

    for p in points:
        if p["kind"] != "TriggerArea" or not p.get("radius"):
            continue
        x, y, z = p["pos"]
        radius = float(p["radius"])
        sample_issues = []
        for k in range(64):
            angle = math.tau * k / 64
            sample = {"pos": (x + math.cos(angle) * radius, y, z + math.sin(angle) * radius)}
            sample_nav = classify_point(sample, polys, index, comp, main_comp)
            if sample_nav["issue"]:
                sample_issues.append(sample_nav["issue"])
        if sample_issues:
            if "OUTSIDE_MESH" in sample_issues:
                p["nav"]["radius_issue"] = "TRIGGER_RADIUS_OUTSIDE_MESH"
            else:
                p["nav"]["radius_issue"] = "TRIGGER_RADIUS_ISOLATED_COMPONENT"
            p["nav"]["radius_bad_samples"] = len(sample_issues)
            p["nav"]["radius_sample_count"] = 64

    issues = []
    for p in points:
        if p["nav"]["issue"]:
            issues.append({
                "issue": p["nav"]["issue"],
                "kind": p["kind"],
                "id": p["id"],
                "obj_id": p["obj_id"],
                "team": p["team"],
                "area_id": p["area_id"],
                "layer": p["layer"],
                "x": p["pos"][0],
                "y": p["pos"][1],
                "z": p["pos"][2],
                "component": p["nav"]["component"],
                "component_size": comp_sizes[p["nav"]["component"]] if p["nav"]["component"] is not None else None,
                "poly": p["nav"]["poly"],
                "nearest_poly": p["nav"]["nearest_poly"],
                "nearest_distance": p["nav"]["nearest_distance"],
                "detail": "",
            })
        if p["nav"].get("radius_issue"):
            issues.append({
                "issue": p["nav"]["radius_issue"],
                "kind": p["kind"],
                "id": p["id"],
                "obj_id": p["obj_id"],
                "team": p["team"],
                "area_id": p["area_id"],
                "layer": p["layer"],
                "x": p["pos"][0],
                "y": p["pos"][1],
                "z": p["pos"][2],
                "component": p["nav"]["component"],
                "component_size": comp_sizes[p["nav"]["component"]] if p["nav"]["component"] is not None else None,
                "poly": p["nav"]["poly"],
                "nearest_poly": p["nav"]["nearest_poly"],
                "nearest_distance": p["nav"]["nearest_distance"],
                "detail": f'radius={p.get("radius")}; bad_samples={p["nav"].get("radius_bad_samples")}/{p["nav"].get("radius_sample_count")}',
            })

    for team in [p for p in points if p["kind"] == "Teams"]:
        bad_children = [c for c in children_by_team.get(team["id"], []) if c["nav"]["issue"]]
        if bad_children:
            issues.append({
                "issue": "TEAM_CHILD_ISSUE",
                "kind": team["kind"],
                "id": team["id"],
                "obj_id": team["obj_id"],
                "team": team["team"],
                "area_id": team["area_id"],
                "layer": team["layer"],
                "x": team["pos"][0],
                "y": team["pos"][1],
                "z": team["pos"][2],
                "component": team["nav"]["component"],
                "component_size": comp_sizes[team["nav"]["component"]] if team["nav"]["component"] is not None else None,
                "poly": team["nav"]["poly"],
                "nearest_poly": team["nav"]["nearest_poly"],
                "nearest_distance": team["nav"]["nearest_distance"],
                "detail": "; ".join(f'{c["kind"]}#{c["id"]}:{c["nav"]["issue"]}' for c in bad_children),
            })

    summary = {
        "navmesh": args.navmesh,
        "scenario": args.scenario,
        "polygon_count": len(polys),
        "component_count": len(comp_sizes),
        "main_component": main_comp,
        "main_component_size": comp_sizes[main_comp],
        "component_sizes_top": sorted(comp_sizes, reverse=True)[:20],
        "point_count": len(points),
        "point_kind_counts": Counter(p["kind"] for p in points),
        "inside_count": sum(1 for p in points if p["nav"]["inside"]),
        "outside_count": sum(1 for p in points if not p["nav"]["inside"]),
        "isolated_count": sum(1 for p in points if p["nav"]["issue"] == "ISOLATED_COMPONENT"),
        "issue_counts": Counter(i["issue"] for i in issues),
    }

    safe_points = []
    for p in points:
        safe_points.append({
            "kind": p["kind"],
            "id": p["id"],
            "obj_id": p["obj_id"],
            "team": p["team"],
            "area_id": p["area_id"],
            "layer": p["layer"],
            "radius": p["radius"],
            "x": p["pos"][0],
            "y": p["pos"][1],
            "z": p["pos"][2],
            "nav": p["nav"],
        })

    Path(args.out_json).write_text(json.dumps({
        "summary": summary,
        "issues": issues,
        "points": safe_points,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    with Path(args.out_csv).open("w", encoding="utf-8-sig", newline="") as f:
        fields = ["issue", "kind", "id", "obj_id", "team", "area_id", "layer", "x", "y", "z", "component", "component_size", "poly", "nearest_poly", "nearest_distance", "detail"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in issues:
            writer.writerow(row)


if __name__ == "__main__":
    main()
