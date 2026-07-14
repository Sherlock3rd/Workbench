# Machinations HTML 复原未保持原始坐标

## 问题
- 用户要求用导出的 Machinations 数据生成 Web 端复原图，用来校验读取是否正确。
- 初版 HTML/Canvas 为了可读性对节点做了语义重排和放大标签，导致节点位置与 Machinations 原图不一致，无法作为“读数是否正确”的校验依据。
- 生成 HTML 时还出现过 JSON HTML 转义和 PowerShell 中文编码问题，导致页面不可用或文案乱码。

## 原因
- 混淆了两类目标：数据校验应优先保持原始坐标；方案讲解才适合重新布局。
- 生成本地 HTML 时没有把 JSON 注入、中文编码、浏览器可解析性作为完成前检查项。

## 修复
- 新增 `artifacts/machinations/albion-machinations-raw-coordinate.html`，节点使用 XML 原始 `x/y/width/height`，仅通过 SVG `viewBox` 和显示缩放调整视野。
- 静态 UI 文案改为 ASCII，节点标签从 JSON 数据以 Unicode 转义注入，避免 PowerShell 管道破坏中文。
- 增加节点点击检查、标签/连线开关、问题边高亮，保证读数校验优先。

## 预防
- 只要用户要求“复原 / 校验 / 看你读得对不对”，必须先提供原坐标视图，不得默认语义重排。
- 可读性优化必须作为可选视图，不能替代原始坐标复原。
- 生成独立 HTML 后至少检查：无 `&quot;` JSON 注入、无 `???` 乱码、数据节点/连线数量与源 XML 解析结果一致。
