# Beagle_MapLP 错误码

| 错误码 | 含义 | 处理方式 |
| --- | --- | --- |
| `LPV-E001` | 根目录或地图配置缺少必要文件 | 确认选择的是 Beagle / 工程根目录，且所选地图对应的 NavMesh 与 LevelPoints 相对路径存在。 |
| `LPV-E002` | 找不到地图生成 helper | 重新使用最新 `Beagle_MapLP` exe，不要移动 exe 解压出的资源。 |
| `LPV-E003` | 找不到 Viewer 脚本或标签资源 | 重新打包或恢复 `viewer-scripts` 资源。 |
| `LPV-E004` | helper 执行失败 | 查看错误页详情和 `beagle-maplp.log`，通常是 JSON/XLSX 格式或路径问题。 |
| `LPV-E005` | helper 未生成 HTML | 查看日志中 helper 输出，确认临时目录可写。 |
| `LPV-E006` | 无法读取页面渲染诊断 | 页面脚本没有正常初始化，查看日志中的 `RENDER_CONSOLE`。 |
| `LPV-E007` | 页面 JavaScript 报错 | 查看错误页详情里的 JS 报错内容。 |
| `LPV-E008` | NavMesh polygon 数量为 0 | 检查 NavMesh JSON 是否包含 `NavMeshPolygons[].Vertexs`。 |
| `LPV-E009` | LevelPoints 点位数量为 0 | 检查 LevelPoints JSON 是否包含 `components[]` 和 `position`。 |
| `LPV-E010` | 刷新源文件失败 | 重新设置根目录后再刷新。 |
| `LPV-E999` | 未分类异常 | 把错误页详情和日志发给维护者。 |

日志会同时尝试写入：

- `%APPDATA%/Beagle_MapLP/beagle-maplp.log`
- `%TEMP%/beagle-maplp.log`
- exe 运行目录下的 `beagle-maplp.log`
