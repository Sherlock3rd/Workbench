# LevelPoints / NavMesh 重新加载索引顺序错误

## 基本信息
- 日期：2026-06-09
- 分类：工具交互 / 数据匹配
- 任务：检查 `levelpoints-navmesh-viewer` 重新加载后点位与底图不匹配的问题

## 问题现象
- 用户反馈重新加载后点位数据和 NavMesh 底图不匹配。
- 重新加载 NavMesh 时，页面先用旧的 `polyIndex` 重新计算点位归属，然后才重建空间索引。
- 同时刷新 NavMesh 和 LevelPoints 时，两个 `FileReader` 异步读取并行触发，LevelPoints 有可能先完成，导致点位基于旧底图索引归类。

## 修复动作
- `parseNavmeshJson()` 中改为先 `rebuildIndexes()`，再遍历点位执行 `classifyPoint()`。
- `refreshSource()` 中当 NavMesh 和 LevelPoints 都已选择时，改为串行读取：先加载 NavMesh，再加载 LevelPoints。
- 曾误加 NavMesh-only 底图旋转控件，用户纠正后改为整体视图变换：NavMesh 和点位必须一起旋转/镜像。默认文件校验结果为原始点位 `895/895` 均在 NavMesh 内，X 镜像、Z 镜像、X/Z 交换后的匹配率明显更低。

## 预防办法
- 任何会改变底图 polygon 数据的 reload，必须先重建 `polyIndex` / `boundaryIndex`，再进行点位分类、问题统计和显示刷新。
- 同时重新加载多个有依赖关系的文件时，不能并发读完各自刷新；底图必须先完成，点位再使用当前底图归类。
- 调试坐标朝向时，默认提供整体旋转/镜像视图，NavMesh 和点位必须一起变换；除非用户明确要求诊断分层，否则不得只旋转或镜像其中一层。
