# NavMesh Viewer 使用旧 analysis JSON 导致点位缺失

## 问题
- 用户反馈 HTML 中缺少很多最新打点。
- 实际磁盘 `LevelPoints.json` 已更新为 `981` 个 components、`965` 个有 position 的点位。
- 当时 `artifacts/levelpoints_navmesh_analysis.json` 和生成 HTML 仍是旧数据：`964` 个 components、`948` 个点位。

## 原因
- 只重新运行了 `visualize_levelpoints_navmesh.py`，但输入仍是旧的 `artifacts/levelpoints_navmesh_analysis.json`。
- `visualize_levelpoints_navmesh.py` 不会重新解析原始 `LevelPoints.json`，它只消费 analysis JSON。

## 修正
- 先重新运行 `analyze_levelpoints_against_navmesh.py`，生成最新 `artifacts/levelpoints_navmesh_analysis.json` 和 CSV。
- 再运行 `visualize_levelpoints_navmesh.py` 生成 HTML。
- 复核后源文件、analysis、HTML 均为 `981 / 965`。

## 预防
- 只要用户质疑点位缺失、源文件可能变化，或重新生成正式 HTML，都必须先核对源 `LevelPoints.json` 与 analysis JSON 数量。
- 不得只用旧 analysis JSON 重新生成 HTML 后声称已导入最新点位。
