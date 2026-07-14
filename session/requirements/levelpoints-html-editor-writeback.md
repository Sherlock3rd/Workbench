# `levelpoints-html-editor-writeback` 需求级会话

## 基本信息
- 工具名称：`levelpoints-html-editor-writeback`
- 当前状态：已初始化 Skill、参考文档和反写脚本
- 责任视角：系统策划在 HTML 地图中编辑 LevelPoints 点位，并生成 Unity 可直接读取的 JSON 文件

## 当前已知输入
- 原始 LevelPoints：`UnityPrj/Assets/LevelEditorV2/Data/Level_9/LevelPoints.json`
- 默认 NavMesh：`data/GameDatas/map_navMesh/40X30_7day_MainLand_navmesh.json`
- HTML 预览来源：`artifacts/levelpoints_navmesh.html`
- 编辑补丁：`artifacts/levelpoints_editor_patch.json`

## 当前已知产出
- Unity 可读编辑结果：`artifacts/LevelPoints.edited.json`
- 写回摘要：`artifacts/levelpoints_editor_writeback_summary.json`
- 编辑后复查分析：`artifacts/levelpoints_edited_analysis.json`
- 编辑后问题列表：`artifacts/levelpoints_edited_issues.csv`

## 当前能力
- 定义 `levelpoints-html-editor-patch/v1` 补丁协议。
- 提供 `scripts/apply_levelpoints_patch.py`，把 HTML 导出的补丁应用到原始 `LevelPoints.json` 结构。
- 默认支持反写 `components[index].position.x/y/z`。
- 默认支持反写白名单内 `serializedData.MonoBehaviour` 字段：`ObjID`、`ObjType`、`AreaID`、`NpcID`、`TeamID`、`BelongToLayerID`、`SubID`。
- 通过 `match.subID`、`match.className`、`match.prefabPath` 防止补丁应用到过期或重排后的源文件。
- 默认输出新 JSON 文件，不直接覆盖 Unity 工程中的源文件。

## 风险与约束
- 静态 HTML 不能静默写任意本地文件；直接保存源文件需要浏览器授权、下载文件或后续本地 exe 包装。
- 不确认 Unity 字段含义时，不得新增任意 MonoBehaviour 字段到编辑白名单。
- 不能把 analysis JSON 的扁平点位记录写回 Unity；必须以原始 `LevelPoints.json` 为基底做局部 patch。
- 写回后必须重新分析编辑后的 JSON，避免旧 analysis 掩盖点位越界或文件结构问题。

## 修改记录
| 日期 | 变更 | 说明 |
| --- | --- | --- |
| 2026-06-09 | 初始化编辑写回 Skill | 新增 Skill 说明、参考文档、agent 入口和 `apply_levelpoints_patch.py`，先固定补丁协议与安全写回流程 |

## 继承指引
- 继承 `rules/rules.md` 中的全部执行原则。
- 开始修改前先检索 `mistakes/` 中与 NavMesh、LevelPoints、HTML 编辑和文件写回相关的记录。
- 只有用户明确要求编辑点位或写回 JSON 时，才使用本 Skill；只读预览仍使用 `levelpoints-navmesh-viewer`。
