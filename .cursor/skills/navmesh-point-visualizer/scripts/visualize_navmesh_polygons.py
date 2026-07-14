#!/usr/bin/env python3
import argparse
import json
from collections import Counter
from pathlib import Path


def as_float(value):
    return float(value or 0)


def polygon_record(poly):
    verts = []
    ys = []
    for vertex in poly.get("Vertexs") or []:
        x = as_float(vertex.get("x"))
        y = as_float(vertex.get("y"))
        z = as_float(vertex.get("z"))
        verts.append([round(x, 4), round(z, 4)])
        ys.append(y)
    return {
        "i": poly.get("PolygonIndex"),
        "area": poly.get("AreaType"),
        "group": poly.get("GroupIndex"),
        "province": poly.get("ProvinceID"),
        "land": poly.get("LandID"),
        "tile": poly.get("TileIndex"),
        "fid": poly.get("FID"),
        "building": poly.get("BuildingType"),
        "y": round(sum(ys) / len(ys), 4) if ys else 0,
        "verts": verts,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--points-analysis", help="Optional analysis JSON from analyze_gmd_points_against_navmesh.py")
    args = parser.parse_args()

    source = Path(args.input)
    data = json.loads(source.read_text(encoding="utf-8-sig"))
    polygons = [polygon_record(poly) for poly in data.get("NavMeshPolygons", [])]

    xs = [x for poly in polygons for x, _ in poly["verts"]]
    zs = [z for poly in polygons for _, z in poly["verts"]]
    ys = [poly["y"] for poly in polygons]
    vertex_counts = [len(poly["verts"]) for poly in polygons]
    group_counts = Counter(poly["group"] for poly in polygons)
    province_counts = Counter(poly["province"] for poly in polygons)
    area_counts = Counter(poly["area"] for poly in polygons)

    bounds = {
        "minX": min(xs),
        "maxX": max(xs),
        "minZ": min(zs),
        "maxZ": max(zs),
        "minY": min(ys),
        "maxY": max(ys),
    }

    stats = {
        "source": str(source),
        "quadrant": data.get("Quadrant"),
        "version": data.get("Version"),
        "mapWidth": data.get("MapWidth"),
        "mapHeight": data.get("MapHeight"),
        "startX": data.get("StartX"),
        "startZ": data.get("StartZ"),
        "polygonCount": len(polygons),
        "vertexCount": sum(vertex_counts),
        "vertexMin": min(vertex_counts),
        "vertexMax": max(vertex_counts),
        "vertexAvg": round(sum(vertex_counts) / len(vertex_counts), 2),
        "bounds": bounds,
        "areaCounts": area_counts.most_common(),
        "groupCounts": group_counts.most_common(),
        "provinceCounts": province_counts.most_common(20),
    }

    points = []
    issue_counts = {}
    if args.points_analysis:
        analysis = json.loads(Path(args.points_analysis).read_text(encoding="utf-8-sig"))
        points = analysis.get("points", [])
        issue_counts = analysis.get("summary", {}).get("issue_counts", {})

    payload = json.dumps({"stats": stats, "polygons": polygons, "points": points, "issueCounts": issue_counts}, separators=(",", ":"))
    html = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>42X42_MainLand NavMesh</title>
<style>
  :root {
    --bg: #f5f7fa;
    --panel: #ffffff;
    --text: #18212f;
    --muted: #607084;
    --line: #d8dee8;
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--text); font-family: "Segoe UI", Arial, sans-serif; }
  .app { height: 100vh; min-height: 680px; display: grid; grid-template-columns: 330px 1fr; }
  aside { background: var(--panel); border-right: 1px solid var(--line); overflow: auto; padding: 18px; }
  main { min-width: 0; display: flex; flex-direction: column; }
  h1 { margin: 0 0 8px; font-size: 19px; line-height: 1.25; letter-spacing: 0; }
  h2 { margin: 18px 0 8px; font-size: 13px; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }
  p { margin: 8px 0; color: var(--muted); font-size: 13px; line-height: 1.5; }
  .metric { display: grid; grid-template-columns: 1fr auto; gap: 8px; padding: 7px 0; border-bottom: 1px solid #edf0f4; font-size: 13px; }
  .metric b { font-weight: 650; }
  .toolbar { min-height: 48px; display: flex; flex-wrap: wrap; align-items: center; gap: 8px; padding: 8px 12px; border-bottom: 1px solid var(--line); background: var(--panel); }
  button, select { border: 1px solid var(--line); border-radius: 6px; background: #fff; color: var(--text); padding: 6px 9px; font-size: 13px; }
  button { cursor: pointer; }
  button:hover { background: #eef2f7; }
  label { display: inline-flex; align-items: center; gap: 6px; font-size: 13px; color: var(--muted); }
  input[type="checkbox"] { width: 16px; height: 16px; }
  .canvas-wrap { position: relative; flex: 1; min-height: 0; background: #e9eef5; overflow: hidden; }
  canvas { width: 100%; height: 100%; display: block; cursor: grab; }
  canvas.dragging { cursor: grabbing; }
  #tip { position: absolute; pointer-events: none; display: none; background: rgba(255,255,255,.96); border: 1px solid var(--line); border-radius: 6px; padding: 8px 9px; font-size: 12px; box-shadow: 0 6px 18px rgba(20,32,48,.14); min-width: 190px; }
  table { width: 100%; border-collapse: collapse; font-size: 12px; }
  td { border-bottom: 1px solid #edf0f4; padding: 5px 0; }
  td:last-child { text-align: right; font-weight: 650; }
  .note { background: #eef9f2; border: 1px solid #b8e0c4; color: #24583a; border-radius: 6px; padding: 10px; font-size: 13px; line-height: 1.45; }
  @media (max-width: 880px) {
    .app { grid-template-columns: 1fr; grid-template-rows: auto 1fr; }
    aside { max-height: 44vh; border-right: 0; border-bottom: 1px solid var(--line); }
  }
</style>
</head>
<body>
<div class="app">
  <aside>
    <h1>42X42_MainLand NavMesh</h1>
    <p>真实 mesh 多边形投影到 X/Z 平面。每个面使用原始 `Vertexs` 绘制，Y 用于高度着色。</p>
    <div class="note">`AreaType` 全部为 4；可视化默认按 `ProvinceID` 着色，能更清楚看到区域切分。</div>
    <h2>概览</h2>
    <div id="metrics"></div>
    <h2>Top ProvinceID</h2>
    <table id="province-table"></table>
    <h2>GroupIndex</h2>
    <table id="group-table"></table>
    <h2>源文件</h2>
    <p id="source"></p>
  </aside>
  <main>
    <div class="toolbar">
      <button id="zoom-in">放大</button>
      <button id="zoom-out">缩小</button>
      <button id="reset">重置视图</button>
      <label>着色
        <select id="color-mode">
          <option value="province">ProvinceID</option>
          <option value="group">GroupIndex</option>
          <option value="height">Height Y</option>
          <option value="sides">Vertex Count</option>
        </select>
      </label>
      <label><input id="stroke-toggle" type="checkbox" checked>边线</label>
      <label><input id="points-toggle" type="checkbox" checked>GMD7 点位</label>
      <label><input id="issues-toggle" type="checkbox">只看问题</label>
      <label><input id="hover-toggle" type="checkbox" checked>悬停信息</label>
      <span id="status"></span>
    </div>
    <div class="canvas-wrap">
      <canvas id="map"></canvas>
      <div id="tip"></div>
    </div>
  </main>
</div>
<script>
const DATA = __PAYLOAD__;
const stats = DATA.stats;
const polygons = DATA.polygons;
const points = DATA.points || [];
const canvas = document.getElementById('map');
const ctx = canvas.getContext('2d');
const tip = document.getElementById('tip');
const modeEl = document.getElementById('color-mode');
const strokeEl = document.getElementById('stroke-toggle');
const pointsEl = document.getElementById('points-toggle');
const issuesEl = document.getElementById('issues-toggle');
const hoverEl = document.getElementById('hover-toggle');
const statusEl = document.getElementById('status');
const palette = ['#2878bd','#36a168','#e6a01b','#cc4c4c','#7b61c9','#2aa6b1','#d45b9f','#6c8a1f','#b7672c','#526a86','#009a78','#b3446c'];
let dpr = Math.max(1, Math.min(2, window.devicePixelRatio || 1));
let view = {};
let dragging = false;
let last = null;
const pointStyles = {
  InteractiveObjs: ['#2f6fed', 4],
  Enemies: ['#d64045', 3.5],
  Teams: ['#f59f00', 6],
  SpawnTravelers: ['#2b8a3e', 7],
  Npcs: ['#7b2cbf', 7],
  TriggerArea: ['#e03131', 5]
};

function fmt(v, n = 2) {
  if (typeof v !== 'number') return String(v);
  return v.toFixed(n);
}

function hashColor(value) {
  const s = String(value);
  let h = 0;
  for (let i = 0; i < s.length; i++) h = ((h << 5) - h + s.charCodeAt(i)) | 0;
  return palette[Math.abs(h) % palette.length];
}

function heightColor(y) {
  const min = stats.bounds.minY;
  const max = stats.bounds.maxY;
  const t = max === min ? 0 : (y - min) / (max - min);
  const r = Math.round(34 + t * 210);
  const g = Math.round(110 + (1 - Math.abs(t - .45) * 1.5) * 85);
  const b = Math.round(190 - t * 150);
  return `rgb(${r},${g},${b})`;
}

function sideColor(count) {
  return hashColor(count + ' sides');
}

function colorFor(poly) {
  const mode = modeEl.value;
  if (mode === 'province') return hashColor(poly.province);
  if (mode === 'group') return hashColor(poly.group);
  if (mode === 'height') return heightColor(poly.y);
  return sideColor(poly.verts.length);
}

function resize() {
  const rect = canvas.getBoundingClientRect();
  canvas.width = Math.max(1, Math.floor(rect.width * dpr));
  canvas.height = Math.max(1, Math.floor(rect.height * dpr));
  draw();
}

function resetView() {
  const b = stats.bounds;
  const w = b.maxX - b.minX;
  const h = b.maxZ - b.minZ;
  const pad = Math.max(w, h) * 0.045;
  view = { x: b.minX - pad, z: b.minZ - pad, w: w + pad * 2, h: h + pad * 2 };
  draw();
}

function worldToScreen(x, z) {
  return {
    x: (x - view.x) / view.w * canvas.width,
    y: (z - view.z) / view.h * canvas.height
  };
}

function screenToWorld(x, y) {
  return {
    x: view.x + x / canvas.width * view.w,
    z: view.z + y / canvas.height * view.h
  };
}

function drawGrid() {
  const step = view.w > 900 ? 100 : view.w > 350 ? 50 : 20;
  ctx.save();
  ctx.lineWidth = 1 * dpr;
  ctx.strokeStyle = '#c9d2de';
  ctx.globalAlpha = .7;
  for (let x = Math.floor(view.x / step) * step; x <= view.x + view.w; x += step) {
    const p = worldToScreen(x, view.z);
    ctx.beginPath();
    ctx.moveTo(p.x, 0);
    ctx.lineTo(p.x, canvas.height);
    ctx.stroke();
  }
  for (let z = Math.floor(view.z / step) * step; z <= view.z + view.h; z += step) {
    const p = worldToScreen(view.x, z);
    ctx.beginPath();
    ctx.moveTo(0, p.y);
    ctx.lineTo(canvas.width, p.y);
    ctx.stroke();
  }
  ctx.restore();
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#edf2f7';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  drawGrid();
  const drawStroke = strokeEl.checked;
  for (const poly of polygons) {
    if (poly.verts.length < 3) continue;
    ctx.beginPath();
    const first = worldToScreen(poly.verts[0][0], poly.verts[0][1]);
    ctx.moveTo(first.x, first.y);
    for (let i = 1; i < poly.verts.length; i++) {
      const p = worldToScreen(poly.verts[i][0], poly.verts[i][1]);
      ctx.lineTo(p.x, p.y);
    }
    ctx.closePath();
    ctx.fillStyle = colorFor(poly);
    ctx.globalAlpha = .72;
    ctx.fill();
    if (drawStroke) {
      ctx.globalAlpha = .42;
      ctx.strokeStyle = '#1f2937';
      ctx.lineWidth = Math.max(.55, Math.min(1.2, 850 / view.w)) * dpr;
      ctx.stroke();
    }
  }
  ctx.globalAlpha = 1;
  drawPoints();
  statusEl.textContent = `X ${fmt(view.x)}..${fmt(view.x + view.w)} / Z ${fmt(view.z)}..${fmt(view.z + view.h)}`;
}

function pointVisible(point) {
  if (!pointsEl.checked) return false;
  if (issuesEl.checked && !(point.nav && (point.nav.issue || point.nav.radius_issue))) return false;
  return true;
}

function drawPoints() {
  if (!pointsEl.checked) return;
  const worldPerPx = view.w / canvas.width;
  for (const point of points) {
    if (!pointVisible(point)) continue;
    const style = pointStyles[point.kind] || ['#111827', 4];
    const p = worldToScreen(point.x, point.z);
    const hasIssue = point.nav && (point.nav.issue || point.nav.radius_issue);
    if (point.kind === 'TriggerArea' && point.radius) {
      ctx.save();
      ctx.beginPath();
      ctx.arc(p.x, p.y, Math.max(4, point.radius / worldPerPx), 0, Math.PI * 2);
      ctx.strokeStyle = hasIssue ? '#111827' : style[0];
      ctx.lineWidth = (hasIssue ? 3 : 1.8) * dpr;
      ctx.setLineDash([7 * dpr, 5 * dpr]);
      ctx.stroke();
      ctx.restore();
    }
    ctx.beginPath();
    ctx.arc(p.x, p.y, (hasIssue ? style[1] + 4 : style[1]) * dpr, 0, Math.PI * 2);
    ctx.fillStyle = hasIssue ? '#111827' : style[0];
    ctx.globalAlpha = hasIssue ? .98 : .88;
    ctx.fill();
    ctx.globalAlpha = 1;
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 1.4 * dpr;
    ctx.stroke();
  }
}

function pointInPoly(point, verts) {
  let inside = false;
  for (let i = 0, j = verts.length - 1; i < verts.length; j = i++) {
    const xi = verts[i][0], zi = verts[i][1];
    const xj = verts[j][0], zj = verts[j][1];
    const intersect = ((zi > point.z) !== (zj > point.z)) && (point.x < (xj - xi) * (point.z - zi) / (zj - zi + 1e-12) + xi);
    if (intersect) inside = !inside;
  }
  return inside;
}

function findPoly(world) {
  for (let i = polygons.length - 1; i >= 0; i--) {
    const poly = polygons[i];
    if (pointInPoly(world, poly.verts)) return poly;
  }
  return null;
}

function findPoint(screen) {
  if (!pointsEl.checked) return null;
  let best = null;
  let bestD = Infinity;
  for (const point of points) {
    if (!pointVisible(point)) continue;
    const p = worldToScreen(point.x, point.z);
    const dx = p.x - screen.x;
    const dy = p.y - screen.y;
    const d = Math.hypot(dx, dy);
    if (d < bestD && d <= 12 * dpr) {
      best = point;
      bestD = d;
    }
  }
  return best;
}

function zoom(factor, screenPoint) {
  const center = screenPoint || { x: canvas.width / 2, y: canvas.height / 2 };
  const before = screenToWorld(center.x, center.y);
  view.w *= factor;
  view.h *= factor;
  const after = screenToWorld(center.x, center.y);
  view.x += before.x - after.x;
  view.z += before.z - after.z;
  draw();
}

canvas.addEventListener('pointerdown', e => {
  dragging = true;
  last = { x: e.clientX, y: e.clientY };
  canvas.classList.add('dragging');
  canvas.setPointerCapture(e.pointerId);
});
canvas.addEventListener('pointermove', e => {
  const rect = canvas.getBoundingClientRect();
  const sx = (e.clientX - rect.left) * dpr;
  const sy = (e.clientY - rect.top) * dpr;
  if (dragging) {
    const dx = (e.clientX - last.x) * dpr / canvas.width * view.w;
    const dz = (e.clientY - last.y) * dpr / canvas.height * view.h;
    last = { x: e.clientX, y: e.clientY };
    view.x -= dx;
    view.z -= dz;
    draw();
    return;
  }
  if (!hoverEl.checked) return;
  const world = screenToWorld(sx, sy);
  const point = findPoint({ x: sx, y: sy });
  if (point) {
    tip.style.display = 'block';
    tip.style.left = `${Math.min(rect.width - 240, e.clientX - rect.left + 12)}px`;
    tip.style.top = `${Math.min(rect.height - 150, e.clientY - rect.top + 12)}px`;
    const issue = point.nav && (point.nav.issue || point.nav.radius_issue) ? (point.nav.issue || point.nav.radius_issue) : 'OK';
    const radiusText = point.nav && point.nav.radius_issue ? `<br>Radius samples: ${point.nav.radius_bad_samples}/${point.nav.radius_sample_count}` : '';
    tip.innerHTML = `<b>${point.kind} #${point.id}</b><br>Issue: ${issue}${radiusText}<br>Obj/Cfg: ${point.obj_id ?? '-'}<br>Team: ${point.team ?? '-'}<br>AreaID: ${point.area_id ?? '-'}<br>Layer: ${point.layer ?? '-'}<br>X/Z/Y: ${fmt(point.x)}, ${fmt(point.z)}, ${fmt(point.y, 3)}<br>Poly: ${point.nav ? point.nav.poly : '-'}`;
    return;
  }
  const poly = findPoly(world);
  if (!poly) {
    tip.style.display = 'none';
    return;
  }
  tip.style.display = 'block';
  tip.style.left = `${Math.min(rect.width - 220, e.clientX - rect.left + 12)}px`;
  tip.style.top = `${Math.min(rect.height - 120, e.clientY - rect.top + 12)}px`;
  tip.innerHTML = `<b>Polygon ${poly.i}</b><br>ProvinceID: ${poly.province}<br>GroupIndex: ${poly.group}<br>AreaType: ${poly.area}<br>Vertexs: ${poly.verts.length}<br>Avg Y: ${fmt(poly.y, 3)}`;
});
canvas.addEventListener('pointerup', e => {
  dragging = false;
  canvas.classList.remove('dragging');
  canvas.releasePointerCapture(e.pointerId);
});
canvas.addEventListener('pointerleave', () => {
  dragging = false;
  canvas.classList.remove('dragging');
  tip.style.display = 'none';
});
canvas.addEventListener('wheel', e => {
  e.preventDefault();
  const rect = canvas.getBoundingClientRect();
  zoom(e.deltaY < 0 ? .86 : 1.16, { x: (e.clientX - rect.left) * dpr, y: (e.clientY - rect.top) * dpr });
}, { passive: false });
document.getElementById('zoom-in').addEventListener('click', () => zoom(.75));
document.getElementById('zoom-out').addEventListener('click', () => zoom(1.33));
document.getElementById('reset').addEventListener('click', resetView);
modeEl.addEventListener('change', draw);
strokeEl.addEventListener('change', draw);
pointsEl.addEventListener('change', draw);
issuesEl.addEventListener('change', draw);

function fillStats() {
  const b = stats.bounds;
  const rows = [
    ['MapWidth / Height', `${fmt(stats.mapWidth)} / ${fmt(stats.mapHeight)}`],
    ['StartX / StartZ', `${fmt(stats.startX)} / ${fmt(stats.startZ)}`],
    ['Polygons', stats.polygonCount],
    ['Vertices', stats.vertexCount],
    ['Vertexs per polygon', `${stats.vertexMin}..${stats.vertexMax}, avg ${stats.vertexAvg}`],
    ['X range', `${fmt(b.minX)}..${fmt(b.maxX)}`],
    ['Z range', `${fmt(b.minZ)}..${fmt(b.maxZ)}`],
    ['Y height', `${fmt(b.minY, 3)}..${fmt(b.maxY, 3)}`],
    ['AreaType', stats.areaCounts.map(x => `${x[0]}: ${x[1]}`).join(', ')]
  ];
  if (points.length) {
    rows.push(['GMD7 points', points.length]);
    const issueText = Object.keys(DATA.issueCounts || {}).length ? JSON.stringify(DATA.issueCounts) : '0';
    rows.push(['Issue points', issueText]);
  }
  document.getElementById('metrics').innerHTML = rows.map(([k, v]) => `<div class="metric"><span>${k}</span><b>${v}</b></div>`).join('');
  document.getElementById('province-table').innerHTML = stats.provinceCounts.map(([k, v]) => `<tr><td>${k}</td><td>${v}</td></tr>`).join('');
  document.getElementById('group-table').innerHTML = stats.groupCounts.map(([k, v]) => `<tr><td>${k}</td><td>${v}</td></tr>`).join('');
  document.getElementById('source').textContent = stats.source;
}

window.addEventListener('resize', resize);
fillStats();
resetView();
resize();
</script>
</body>
</html>
"""
    Path(args.output).write_text(html.replace("__PAYLOAD__", payload), encoding="utf-8")


if __name__ == "__main__":
    main()
