# Machinations 行为节点误画成 Source

## 问题
- Albion 讨论重绘图中，`PvE 击杀/开箱` 被画成 `Source`。
- 这会误导为 PvE 行为本身凭空生成装备资源，导致 `PvE 击杀/开箱 -> 野怪掉落装备库` 被错误画成 Resource 资源流。

## 原因
- 混淆了“行为触发”和“资源来源”。
- `Source` 应只用于真实生成资源的节点；玩家行为、击杀、开箱、战斗判定这类流程节点更适合用 `Gate` 或 `Register`，再用 `State` 线触发资源池流出。

## 修复
- 将 `PvE 击杀/开箱` 从 `Source` 改为 `Gate`。
- 将 `PvE 击杀/开箱 -> 野怪掉落装备库` 从 `Resource` 改为 `State`，备注改为 `触发掉落抽取`，数值保留 `1`。
- 保留 `野怪掉落装备库 -> PvE 装备掉落` 为 `Resource`，表示装备真正从掉落库流出。
- 测试增加约束：讨论重绘图唯一 Source 必须是 `资源采集`。

## 预防
- 画 Machinations 图时先判断节点是否真的生成资源：
  - 生成资源：可用 `Source`。
  - 搬运、存放、消耗资源：用 `Pool`、`Converter`、`Drain` 等。
  - 行为、判定、触发、影响：优先用 `Gate` / `Register` + `State` 线。
