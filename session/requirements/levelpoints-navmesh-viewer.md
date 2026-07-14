# `levelpoints-navmesh-viewer` 需求级会话

## 基本信息
- 工具名称：`levelpoints-navmesh-viewer`
- 当前状态：已恢复并完成默认文件重新生成验证
- 责任视角：系统策划检查大地图 NavMesh 分区与 Unity LevelEditor 点位分布

## 当前已知输入
- NavMesh 默认路径：`data/GameDatas/map_navMesh/40X30_7day_MainLand_navmesh.json`
- LevelPoints 默认路径：`UnityPrj/Assets/LevelEditorV2/Data/Level_9/LevelPoints.json`
- 标签配置：`.cursor/skills/levelpoints-navmesh-viewer/scripts/default_point_labels.json`
- 交互物文本表：`data/GameDatas/datas/InteractiveObj.xlsx`
- 区域配置表：`data/GameDatas/datas/area_config.xlsx`

## 当前已知产出
- 交互式 HTML：`artifacts/levelpoints_navmesh.html`
- 分析 JSON：`artifacts/levelpoints_navmesh_analysis.json`
- 问题 CSV：`artifacts/levelpoints_navmesh_issues.csv`

## 当前能力
- 读取 NavMesh 与 `LevelPoints.json`，生成可缩放、可搜索、可筛选点位图层的 HTML 预览。
- 校验点位是否落在 NavMesh 内，以及是否处于非主连通分区。
- 支持 `极简模式`、`完整 NavMesh`、`分区边界简化` 三种底图模式；`极简模式` 保留大外轮廓连通块，并按边界侧连通块的包围面积 `< 200` 隐藏内部小围合和原始边匹配中表现为 `outer` 的小碎边。
- 点位按原始类型固定颜色显示，并使用更醒目的光晕、白底圈、彩色核心和深色描边。
- 不再暴露“原文件索引”侧边栏功能、按索引分组和按索引搜索；错误检查列表内部可保留 `components[]` 信息用于定位问题点。
- 支持显示当前 NavMesh / LevelPoints 源路径，通过浏览器文件选择器更改源文件，并用“刷新重新加载”重新读取最近授权选择的本地文件；重载过程显示进度条和当前阶段。
- HTML 内“刷新重新加载”在拿到授权源文件后，必须重做浏览器内分析流程：解析 NavMesh、重建空间索引、解析原始 `LevelPoints.json`、归一化点位、重新判定 NavMesh 归属、刷新筛选统计和地图，不得复用过期 analysis。
- 支持整体旋转（`0°`、`90°`、`180°`、`270°`）和整体镜像（无、左右、上下、左右+上下），默认使用 `上下镜像` 让世界 `Z` 递增方向按地图习惯向上显示；NavMesh 和点位必须一起变换，且不改变原始坐标与 NavMesh 判定。
- NavMesh 着色仅保留 `ProvinceID`、区域类型、`Height Y`；区域类型通过 `ProvinceID -> area_config.INT_areaID` 匹配，并根据 `INT_pvpType`、`INT_gveType` 判定 `PVP区域`、`特殊区域` 或 `普通区域`。
- 支持“合法性检查”面板：默认检查点位是否落在当前 NavMesh 上；可选检查 `传送车站` 是否位于 `PVP区域`；检查过程显示进度与当前检查项，结束后在地图上高亮错误点，并输出可点击定位的错误列表。
- 支持“车站距离检查”面板：识别 `obj_display_name` 含 `传送车站` 的点位，始终基于完整 `NavMeshPolygons` polygon 共边邻接图用多源 Dijkstra 计算每个车站到最近另一个车站的近似最短路径距离，不能使用“分区边界简化”或“极简模式”的显示结果参与计算；记录沿 NavMesh polygon 中心链路的折线路线，合并互为最近邻的重复路线，按玩家速度 `5.8m/s` 计算移动耗时，在地图上只绘制这些最近邻路线，并高亮其中距离最大的 10 条路线与距离/耗时标签。
- 已新增 Electron 桌面封装工程 `tools/levelpoints-electron-viewer/`：使用系统窗口承载现有 HTML 地图，用户只选择 Beagle / 工程根目录，Electron 主进程按固定相对路径自动定位 NavMesh、LevelPoints、InteractiveObj 和 area_config，并通过 IPC 支持按路径刷新读取，不再依赖浏览器本地文件授权。

## 风险与约束
- “停车位、矿区、NPC”等业务标签尚未确认对应的 `ObjID` 或 `ObjType`，当前只做保守分类。
- 静态 HTML 不能绕过浏览器权限直接按磁盘路径静默读取本地文件；默认路径只是生成来源和显示信息，不等于浏览器已有读盘权限。静态文件模式下，没有授权文件时，“刷新重新加载”应主动弹出文件选择器让用户选择最新 `LevelPoints.json`，选择后立即重跑浏览器内点位分析；选择过本地文件后，优先通过 File System Access API 文件句柄重新 `getFile()` 读取磁盘最新内容，不支持文件句柄的浏览器只能重读最近授权的 `File` 对象，并需要在状态中说明限制。若需要“点刷新直接按路径读”，后续通过 exe 封装成本地应用解决。
- Electron 桌面版允许按根目录 + 固定相对路径直接读取，但只负责读取、预览、刷新和检查；点位编辑与写回仍归 `levelpoints-html-editor-writeback` 管理。
- 用户只要求源文件路径更改和刷新时，不得擅自加入点位内容编辑、写回源文件或导出改后 JSON。

## 修改记录
| 日期 | 变更 | 说明 |
| --- | --- | --- |
| 2026-06-09 | 初始化 `levelpoints-navmesh-viewer` | 新增项目级 Skill、agent 入口、分析脚本、可视化脚本、默认标签配置，并完成默认文件验证 |
| 2026-06-09 | 优化底图与点位显示 | 新增底图模式、空间索引、原始类型筛选、点位类型颜色和更醒目的点位渲染 |
| 2026-06-09 | 增加源索引和源文件重载 | 显示 `components[]` 原文件索引；支持按索引定位和复制；显示并通过文件选择器更改 NavMesh / LevelPoints 源文件；支持刷新重新加载最近授权文件 |
| 2026-06-09 | 修正误解并恢复文件 | 移除误加的点位内容编辑入口，恢复 `SKILL.md`、`agents/openai.yaml`、脚本和默认标签文件 |
| 2026-06-09 | 恢复并修正极简模式面积过滤 | 恢复 `boundaryComponentArea` 预计算和前端重载后的同等计算；改为按边界两侧分区签名分别计算连通块面积，并对原始 `outer` 小碎边也按 `< 200` 隐藏 |
| 2026-06-09 | 修正重载匹配问题并增加整体变换 | 更换 NavMesh 时先重建空间索引再重算点位归属；同时刷新 NavMesh 和 LevelPoints 时改为先读 NavMesh 再读 LevelPoints；新增整体旋转和整体镜像控件；默认文件原始点位 `895/895` 均在 NavMesh 内，镜像或 X/Z 交换匹配率明显更低 |
| 2026-06-09 | 调整 NavMesh 着色模式 | 移除 `GroupIndex`、connected component、vertex count 着色；新增基于 `area_config.xlsx` 的区域类型着色，并将记录路径改为相对 Beagle 根目录 |
| 2026-06-09 | 增加合法性检查面板 | 新增启动检查按钮、检查项勾选、进度条、当前检查项状态、错误点地图高亮和可点击定位的错误列表；默认启用点位/NavMesh 检查，可选传送车站/PVP 检查 |
| 2026-06-09 | 移除原文件索引面板并加强重载 | 去掉原文件索引定位/复制面板、按索引分组和按索引搜索；源文件刷新新增进度条，并优先使用文件句柄读取磁盘最新内容 |
| 2026-06-09 | 修正旧 analysis 导致点位缺失 | 重新运行分析脚本导入最新 `LevelPoints.json`，源文件、analysis、HTML 均更新为 `981` 个 components、`965` 个有效点位；以后正式生成 HTML 前必须先确认 analysis JSON 未过期 |
| 2026-06-09 | 集成刷新分析流程 | `visualize_levelpoints_navmesh.py` 新增 `--levelpoints`，生成 HTML 前可自动重跑 analysis；HTML 刷新阶段显示读取、解析 NavMesh、分析 LevelPoints、刷新地图等进度 |
| 2026-06-09 | 修正刷新按钮无授权行为 | 未授权源文件时不再恢复旧快照，而是由“刷新重新加载”直接弹出 `LevelPoints.json` 文件选择器，并在选择后马上重跑点位分析 |
| 2026-06-09 | 改为 exe 封装方向 | 直接按配置路径读取文件的能力后续通过 exe 封装解决 |
| 2026-06-09 | 增加车站距离检查 | 新增每个传送车站到最近传送车站的 NavMesh 邻接近似最短路计算、移动耗时计算、地图连线和最长 10 条最近邻连线高亮展示 |
| 2026-06-09 | 优化车站距离算法 | 将逐车站 Dijkstra 改为多源 Dijkstra，记录不同车站扩散相遇候选，为每个车站保留最近邻并合并重复无向路线；绘制时沿 NavMesh polygon 中心链路显示折线，不再画端点直线 |
| 2026-06-09 | 明确车站距离计算基准 | 车站距离检查始终使用完整 `NavMeshPolygons` 构建寻路图，不受“极简模式”或“分区边界简化”底图显示影响 |
| 2026-06-09 | 新增 Electron 桌面应用封装 | 新增 `tools/levelpoints-electron-viewer/`，使用 Electron 系统窗口加载现有 Viewer HTML，通过 IPC 支持原生文件选择和按路径刷新读取最新 NavMesh / LevelPoints |
| 2026-06-09 | 简化 Electron 路径选择 | 桌面版从逐个选择 NavMesh / LevelPoints 改为只设置工程根目录，其他输入按默认相对路径自动查找 |

## 继承指引
- 继承 `rules/rules.md` 中的全部执行原则。
- 开始修改前先检索 `mistakes/` 中与规则、会话、Skill 搭建和 NavMesh viewer 相关的记录。
- 未确认业务标签映射前，不得把 `ObjID` 或 `ObjType` 主观命名为停车位、矿区等业务类型。
