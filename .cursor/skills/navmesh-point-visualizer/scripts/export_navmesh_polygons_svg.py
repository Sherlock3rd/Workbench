#!/usr/bin/env python3
import argparse
import html
import json
from pathlib import Path


PALETTE = [
    "#2878bd", "#36a168", "#e6a01b", "#cc4c4c", "#7b61c9", "#2aa6b1",
    "#d45b9f", "#6c8a1f", "#b7672c", "#526a86", "#009a78", "#b3446c",
]


def color_for(value):
    text = str(value)
    h = 0
    for ch in text:
        h = ((h << 5) - h + ord(ch)) & 0xFFFFFFFF
    return PALETTE[h % len(PALETTE)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--mode", choices=["province", "group"], default="province")
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8-sig"))
    polygons = data.get("NavMeshPolygons", [])
    xs, zs = [], []
    for poly in polygons:
        for vertex in poly.get("Vertexs") or []:
            xs.append(float(vertex.get("x", 0)))
            zs.append(float(vertex.get("z", 0)))

    min_x, max_x = min(xs), max(xs)
    min_z, max_z = min(zs), max(zs)
    pad = max(max_x - min_x, max_z - min_z) * 0.04
    view_box = f"{min_x - pad:.2f} {min_z - pad:.2f} {(max_x - min_x) + pad * 2:.2f} {(max_z - min_z) + pad * 2:.2f}"

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_box}" width="1400" height="1400">',
        '<rect width="100%" height="100%" fill="#edf2f7"/>',
        '<style>.grid{stroke:#c9d2de;stroke-width:.55}.poly{stroke:#1f2937;stroke-width:.28;stroke-opacity:.34;fill-opacity:.72}</style>',
    ]

    for x in range(int(min_x // 100 * 100), int(max_x + 101), 100):
        parts.append(f'<line class="grid" x1="{x}" y1="{min_z - pad:.2f}" x2="{x}" y2="{max_z + pad:.2f}"/>')
    for z in range(int(min_z // 100 * 100), int(max_z + 101), 100):
        parts.append(f'<line class="grid" x1="{min_x - pad:.2f}" y1="{z}" x2="{max_x + pad:.2f}" y2="{z}"/>')

    for poly in polygons:
        verts = poly.get("Vertexs") or []
        if len(verts) < 3:
            continue
        key = poly.get("ProvinceID") if args.mode == "province" else poly.get("GroupIndex")
        points = " ".join(f'{float(v.get("x", 0)):.4f},{float(v.get("z", 0)):.4f}' for v in verts)
        title = (
            f'Polygon {poly.get("PolygonIndex")} | Province {poly.get("ProvinceID")} | '
            f'Group {poly.get("GroupIndex")} | AreaType {poly.get("AreaType")} | Vertexs {len(verts)}'
        )
        parts.append(f'<polygon class="poly" points="{points}" fill="{color_for(key)}"><title>{html.escape(title)}</title></polygon>')

    parts.append("</svg>")
    Path(args.output).write_text("\n".join(parts), encoding="utf-8")


if __name__ == "__main__":
    main()
