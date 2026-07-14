# Machinations 抓取数据到 Web 复原页规范

## 目标

将 Machinations.io 浏览器端抓取到的图数据转为本地可审阅的 HTML 复原页，用于验证 AI 是否正确读取图结构，并辅助定位错误节点与连线。

本规范优先服务“读数校验”，因此默认视图必须保持 Machinations XML 中的原始节点坐标，不得用语义重排替代原坐标复原。

## 输入

- 抓取文件：`artifacts/machinations/machinations-capture.json`
- 必需响应：`https://my.machinations.io/diagram/open/<diagram_id>`
- 必需字段：响应 JSON 中的 `content.xml`
- XML 格式：`mxGraphModel`

## 半自动更新流程

浏览器抓取脚本：

- `tools/machinations/browser_capture_snippet.js`

本地生成脚本：

- `tools/machinations/update_machinations_preview.py`

推荐流程：

1. 在已登录的 Machinations 图页面打开浏览器 DevTools Console。
2. 粘贴并运行 `tools/machinations/browser_capture_snippet.js`。
3. 浏览器会下载 `machinations-capture.json`。
4. 将下载文件覆盖到 `artifacts/machinations/machinations-capture.json`。
5. 在仓库根目录运行：

```powershell
py -3 tools/machinations/update_machinations_preview.py --capture artifacts/machinations/machinations-capture.json --output artifacts/machinations/albion-machinations-raw-coordinate.html
```

6. 重新打开或刷新 `artifacts/machinations/albion-machinations-raw-coordinate.html`。

该流程只使用当前浏览器登录态，不需要在聊天或脚本中暴露 Machinations API token。

若用户重新导出数据，必须重新读取 `machinations-capture.json` 的源 XML，不得复用旧的中间分析结果。

## 数据解析

节点类型映射：

- `mxPoolShapeCell` -> `Pool`
- `mxSourceShapeCell` -> `Source`
- `mxConverterShapeCell` -> `Converter`
- `mxGateShapeCell` -> `Gate`
- `mxMachinationRegisterCell` -> `Register`
- `mxDrainShapeCell` -> `Drain`

节点字段：

- `id`
- `value` 作为显示标签
- `mxGeometry.x`
- `mxGeometry.y`
- `mxGeometry.width`
- `mxGeometry.height`
- `formula` 或 `formulaValue`
- `activation`

连线类型映射：

- `mxResourceConnectionCell` -> `resource`
- `mxStateConnectionCell` -> `state`

连线字段：

- `id`
- `source`
- `target`
- `value` 作为显示标签
- `formulaValue` 或 `formula`
- `resource`

仅绘制 `source` 和 `target` 都能匹配到已解析节点的连线；缺少节点端点的 XML 元素可以统计但不应强行画入节点图。

## Web 复原页要求

输出文件：

- `artifacts/machinations/albion-machinations-raw-coordinate.html`

显示原则：

- 节点必须使用 XML 原始 `x/y/width/height`。
- 页面只能通过 SVG `viewBox`、显示比例和滚动容器调整视野。
- 默认不得做语义重排。
- 如果需要“整理视图”或“目标结构视图”，必须作为独立可选视图，并明确标注不是原坐标校验图。
- 可选讨论视图可以重绘为接近 Machinations 手工建图习惯的结构图，但必须保留原坐标复原图作为默认视图，并在页面解释重绘原因与口径变化。

节点形状：

- `Pool`：圆或椭圆
- `Source`：右向箭头
- `Converter`：圆角矩形
- `Gate`：菱形
- `Register`：直角矩形
- `Drain`：梯形或漏斗形

连线样式：

- 资源流：实线
- 状态/影响线：虚线
- 优先检查的问题边：红色高亮

交互要求：

- 鼠标左键拖动画布，实际操作外层滚动容器。
- 滑杆缩放显示比例，不改变原始节点坐标。
- 可开关节点标签、边标签、状态线、资源线。
- 点击节点显示原始 ID、类型、坐标、公式和自动触发状态。
- 拖动画布时不应误触发节点选择。
- 若页面提供多个视图，视图切换后缩放、拖拽、标签开关、连线类型开关、节点点击详情仍必须可用。

## 图例说明

HTML 中必须展示以下图例：

- 图例必须放在画布容器上方，不得以浮层形式覆盖画布。
- 图例必须包含节点形状和连线样式的小图形示例，不能只有文字说明。
- 节点形状与 Machinations 类型的对应关系。
- 资源流与状态线的区别。
- 红色高亮的含义。
- 坐标保真规则：节点使用原始 XML 坐标，页面只做显示层缩放和平移。
- 基本操作：左键拖拽、点击节点、缩放、标签开关。

## 验证清单

生成 HTML 后至少验证：

- `machinations-capture.json` 中成功解析出节点数和可绘制连线数。
- HTML 内嵌数据包含关键节点原坐标，例如 `1148`、`1151`。
- HTML 不包含坏的 JSON 注入，如将数据写成 `&quot;` 后再解析。
- HTML 不包含 `???` 编码乱码。
- 打开后默认展示的是原坐标复原图，而不是整理图。
- 本地脚本输出的节点数、可绘制连线数与当前抓取文件一致。

## 当前 Albion 样例

当前导出样例：

- 节点数：`78`
- 可绘制连线数：`99`
- 原始复原文件：`artifacts/machinations/albion-machinations-raw-coordinate.html`
- 当前 HTML 额外提供 `讨论重绘图` 视图，用于讨论 Albion 后半段市场、黑市、PvE、PvP 与公会分工流向；该视图不是原坐标校验图。

已知优先检查项：

- `1164`、`1166`：`成交撮合` 同时输出到 PvP 与 PvE，可能导致装备复制。
- `1170`、`1171`：费用 Drain 以负数回流到银币池，方向不符合 sink 语义。
- 多个黑市相关 Pool 重复，建议后续整理为 `Converter + Drain + Register`。
