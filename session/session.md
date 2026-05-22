# 项目总控会话

## 项目概览
- 项目名称：Workbencch
- 项目目标：建立一个可持续沉淀策划工具、规则和复盘记录的工作台项目。
- 当前阶段：基础框架已初始化，`ux-text-requirements-generator` 已完成首轮测试
- 首个接入工具：`ux-text-requirements-generator`

## 当前全局状态
- 规则状态：已初始化 `rules/rules.md`
- 会话状态：已建立全局会话与首个需求级会话
- 错题体系：已建立目录与记录模板
- 术语体系：已初始化 `docs/beagle_glossary.md`
- 规范归档：已归档 `spec/rules-bootstrap-spec.md`
- 环境状态：`ux-text-requirements-generator` 依赖已安装，并通过 Python 导入校验
- 测试状态：已基于 `uxbench/pic/kvktest.jpg` 用新版脚本重新生成草案与 Excel
- 飞书状态：已完成 Feishu CLI 安装、skills 安装、配置初始化、用户态授权与云文档创建验证

## 目录总账
- `rules/`：项目规则、对话规范、执行原则
- `session/`：项目级与需求级状态跟踪
- `session/requirements/`：按工具或需求拆分的专项会话
- `mistakes/`：错题记录、分类归纳与防呆清单
- `spec/`：基础规范归档
- `docs/`：术语表与补充文档
- `.cursor/skills/ux-text-requirements-generator/`：首个已完成的 UX 转文本需求工具

## 工具总账
| 工具名 | 状态 | 说明 | 下一步 |
| --- | --- | --- | --- |
| `ux-text-requirements-generator` | 已接入，首轮测试完成 | 已完成环境校验，并使用 `.cursor/skills/ux-text-requirements-generator/scripts/build_ux_requirement_workbook.py` 重新生成 Excel | 继续补样例表与规则文档，提升识别准确度 |
| `planning-analytics-tracking` | 已接入，待实文档验证 | Cursor 项目级 Skill，读取飞书策划案并生成数据打点需求，优先尝试原生数据打点页签，不支持时回退为 `## 数据打点` 区块 | 使用真实策划案链接验证读取、页签调研、写回流程 |
| `planning-audio-requirements` | 已接入，持续纠偏中 | Cursor 项目级 Skill，读取飞书策划案和相关页签，先输出策划必看，再整理音乐、音效、配音需求，并内置音频需求页签固定样式规范 | 继续用真实策划案验证音乐判定边界、音效判定边界、复合功能拆分、配音需求抽取与写回格式 |
| `planning-announcement-requirements` | 已接入，ROK 已获文案认可 | Cursor 项目级 Skill，读取飞书策划案或详细方案，确认项目后生成面向玩家的版本公告文案；当前重点支持 ROK，COD/Beagle 仍需提供对应术语表和训练样本提升准确率 | 继续沉淀真实 ROK 案例；待 COD/Beagle 术语表和公告样本齐备后再扩展对应项目准确率 |

## 变更记录
| 日期 | 事项 | 影响范围 | 备注 |
| --- | --- | --- | --- |
| 2026-04-02 | 初始化项目基础目录与规则框架 | 全项目 | 基于 `rules-bootstrap-spec` 创建 |
| 2026-04-02 | 接入 `ux-text-requirements-generator` 作为首个工具对象 | `.cursor/skills/ux-text-requirements-generator/`、`session/requirements/uxskill.md` | 后续进行环境验证与工具测试 |
| 2026-04-02 | 完成 `ux-text-requirements-generator` 环境搭建 | `.cursor/skills/ux-text-requirements-generator/` | 使用 `py -3` 安装依赖并完成导入校验 |
| 2026-04-02 | 完成 `uxskill` 首轮测试 | `uxbench/output/`、`tools/build_ux_requirement_workbook.py` | 生成配置、扁平化草案与 Excel 产物 |
| 2026-04-02 | 改用新版 workbook 脚本重生成 | `uxbench/output/`、`.cursor/skills/ux-text-requirements-generator/scripts/build_ux_requirement_workbook.py` | 已删除上一版输出，并基于新脚本重新导出 |
| 2026-04-02 | 新增 Feishu CLI 部署与文档操作规范 | `spec/feishu-cli-deployment-and-doc-ops-spec.md` | 固化安装、授权、建文档与建文件夹权限差异 |
| 2026-05-11 | 新增策划案数据打点 Skill | `.cursor/skills/planning-analytics-tracking/`、`session/requirements/planning-analytics-tracking.md` | 固化飞书策划案读取、埋点表生成、原生页签优先与章节回退流程 |
| 2026-05-11 | 纠偏数据打点输出格式 | `.cursor/skills/planning-analytics-tracking/`、`mistakes/data-tracking-output-format.md`、`session/requirements/planning-analytics-tracking.md` | 改为块状表结构，公共维度单独成块，去掉字段归属与逐行负责策划 |
| 2026-05-12 | 补充数据打点二次询问规范 | `.cursor/skills/planning-analytics-tracking/`、`session/requirements/planning-analytics-tracking.md` | 对范围、归属、公共维度、枚举、写回方式、负责人等关键不确定点要求先确认 |
| 2026-05-12 | 新增美术需求读取黑名单 | `.cursor/skills/planning-analytics-tracking/`、`mistakes/data-tracking-art-requirements-source.md`、`session/requirements/planning-analytics-tracking.md` | 美术/视觉/资源/动效/音频等中间交付默认不作为功能实现口径生成打点字段 |
| 2026-05-12 | 修正数据打点表名与字段类型口径 | `.cursor/skills/planning-analytics-tracking/`、`session/requirements/planning-analytics-tracking.md` | 表名默认不用下划线，字段类型统一只输出 string |
| 2026-05-12 | 参考数据组埋点方案 Skill 并纠偏 | `.cursor/skills/planning-analytics-tracking/`、`session/requirements/planning-analytics-tracking.md` | 仅保留“字段服务明确指标”原则，撤回记录时机、端侧建议、关联说明等数据组方案字段 |
| 2026-05-12 | 增加打点需求描述总览格式 | `.cursor/skills/planning-analytics-tracking/`、`session/requirements/planning-analytics-tracking.md` | 输出最前面增加功能名、需求描述、目的三列表，用于先汇总参与率、胜率、战斗时间等指标问题 |
| 2026-05-12 | 修正需求描述总览行数规则 | `.cursor/skills/planning-analytics-tracking/`、`session/requirements/planning-analytics-tracking.md` | 总览行数按文档实际指标决定，不受参考示例三行限制 |
| 2026-05-12 | 补充详细方案图片读取规则 | `.cursor/skills/planning-analytics-tracking/`、`mistakes/data-tracking-missed-image-reading.md`、`session/requirements/planning-analytics-tracking.md` | 核心方案在截图/长图/流程图中时必须先读图，无法识别则二次询问 |
| 2026-05-12 | 新增 PA 广告打点需求文档 | `docs/ROK_火山危机_PA广告打点需求.md` | 基于飞书原始设计文档与本地最终 HTML 文件生成 PA 试玩漏斗、选择、交互和结局 CTA 打点需求 |
| 2026-05-12 | 新增策划案音频需求 Skill | `.cursor/skills/planning-audio-requirements/`、`session/session.md` | 固化飞书策划案读取、关键场景屏音乐需求判断、音效需求提示文本与参考页签样式回退规则 |
| 2026-05-13 | 纠偏音频需求新场景与音效拆分规则 | `.cursor/skills/planning-audio-requirements/`、`mistakes/audio-requirements-missed-new-scene-and-sfx-splitting.md`、`session/session.md` | 新场景进入需考虑音乐循环；音效需求按功能拆分，覆盖点击、交互、动画和反馈 |
| 2026-05-13 | 补充音频需求配音规则 | `.cursor/skills/planning-audio-requirements/`、`mistakes/audio-requirements-missed-voiceover-dialogue.md`、`session/session.md` | 方案中出现对话、台词或带说话人的提示时，单独输出配音需求并列明说话人、情绪、场景触发 |
| 2026-05-13 | 补充音乐需求判定条件 | `.cursor/skills/planning-audio-requirements/`、`session/session.md` | 增加战斗/副本、活动/节日、叙事/剧情、视频演示、不确定全屏系统界面的音乐需求判断规则 |
| 2026-05-13 | 补充音效需求判定条件 | `.cursor/skills/planning-audio-requirements/`、`session/session.md` | 增加页面 UI 交互、场景氛围音、动画与特效动作反馈、视频音效的判断规则 |
| 2026-05-13 | 补充配音需求判定条件 | `.cursor/skills/planning-audio-requirements/`、`session/session.md` | 明确角色或系统有文案/台词且需要发声讲话时，即纳入配音需求 |
| 2026-05-13 | 补充音频需求前置说明格式 | `.cursor/skills/planning-audio-requirements/`、`session/session.md` | 输出最前面增加提需求准备说明，提示策划准备可视化参考、情绪/竞品参考，并及时同步前置变更 |
| 2026-05-13 | 固化音频需求页签样式规范 | `.cursor/skills/planning-audio-requirements/`、`session/session.md` | 从参考页签导出 xlsx 解析真实样式，记录标题、分区、条目、字段标签与正文的颜色、字体、布局规则 |
| 2026-05-13 | 修正音频需求样式主黄色 | `.cursor/skills/planning-audio-requirements/`、`session/session.md` | 标题与黄色分区主色统一改为 `#FAC603`，浅黄色变体保留为 `#FAF1D1` |
| 2026-05-13 | 修正音频需求前置标题与对齐 | `.cursor/skills/planning-audio-requirements/`、飞书 `Li6mQ` 页签、`session/session.md` | 将 `提需求准备说明` 改为 `策划必看`，并重设页签文本对齐规则 |
| 2026-05-13 | 纠偏音频需求字号、深灰底字色与字段标签列 | `.cursor/skills/planning-audio-requirements/`、`mistakes/audio-requirements-style-and-field-label-layout.md`、飞书 `Li6mQ` 页签、`session/session.md` | 深灰底 `#3A3E43` 固定白字，恢复大标题 36 号加粗，字段标签从 `B` 列移到 `C` 列 |
| 2026-05-13 | 生成小队系统音频需求页签 | 飞书 `PwD6siU0HhfVyvtD48mczKZSnJb` / `2caZoc`、`session/session.md` | 基于小队-副本界面开发详细方案、匹配规则、副本战斗预期与界面文本，生成 `音频需求` 页签，包含音乐需求、音效需求与待确认事项 |
| 2026-05-13 | 修复小队系统音频需求文本可见性与行高 | `.cursor/skills/planning-audio-requirements/`、`mistakes/audio-requirements-style-and-field-label-layout.md`、飞书 `2caZoc` 页签、`session/session.md` | 为长文本手动加入换行，并按实际内容行重设行高，避免视觉截断和空白行过高 |
| 2026-05-13 | 新增飞书文档写入特别流程规范 | `spec/feishu-document-writing-special-flow-spec.md`、`rules/rules.md`、`.cursor/skills/planning-audio-requirements/`、`.cursor/skills/planning-analytics-tracking/`、`session/session.md` | 将文本缺失、行高、合并错位、颜色字号覆盖、固定行号偏移等问题沉淀为通用飞书写入前置流程，供所有写回飞书的 Skill 调用 |
| 2026-05-13 | 修正音频配音需求气泡窗口径 | `.cursor/skills/planning-audio-requirements/`、`mistakes/audio-requirements-missed-voiceover-dialogue.md`、飞书 `2caZoc` 页签、`session/session.md` | 普通 UI/IM/组队申请气泡窗文案不默认作为配音需求，除非明确要求语音播报或角色/系统发声 |
| 2026-05-13 | 收紧小队系统音频需求行高 | `spec/feishu-document-writing-special-flow-spec.md`、飞书 `2caZoc` 页签、`session/session.md` | 将两行长文本行高从偏高值收紧到约 45pt，较长关键交互保留约 51pt，并补充导出复查真实行高要求 |
| 2026-05-13 | 补充飞书表格模拟 autofit 行高流程 | `spec/feishu-document-writing-special-flow-spec.md`、`.cursor/skills/planning-audio-requirements/`、飞书 `2caZoc` 页签、`session/session.md` | 飞书 API 未确认支持真正自动适应行高，改为完成后读取所有行并按显式换行/文本长度逐行计算 `fixedSize`，再导出复查 |
| 2026-05-14 | 生成联盟数据打点需求页签 | 飞书 `B6B4sUCt7hV4qktXqGacaiYqnCb` / `1Zi77i`、`session/session.md` | 基于 `详细方案`、联盟礼物数值与投放、联盟权限、报错码页签生成 `数据打点` 页签；跳过 `美术需求`，并导出 xlsx 复查标题、行高、列宽与样式 |
| 2026-05-15 | 生成任务系统数据打点需求页签 | 飞书 `NM4jsTdlmhAg3ytvX0hcTpoqnpe` / `DhL5C`、`session/session.md` | 基于 `beagle - 任务系统` 的任务底层逻辑、任务类型、显示、引导、完成条件、FTE/分线岛主线等页签生成 `数据打点` 页签，并导出 xlsx 复查标题、行高、列宽与样式 |
| 2026-05-15 | 生成日课系统数据打点需求页签 | 飞书 `O5EzsKENghvahQt1uJycn6m1n7g` / `2zoq1G`、`session/session.md` | 基于 `beagle - 日课系统` 的 `详案（7日版本）`、UI需求和文本需求生成 `数据打点` 页签；`殊途同归方向` 标注 7 日不做，仅作为待确认后续方向，并导出 xlsx 复查标题、行高、列宽与样式 |
| 2026-05-15 | 生成图鉴系统数据打点需求页签 | 飞书 `DCyKsIVbyhkfxWtY0elc1BmynTe` / `3NPYRy`、`session/session.md` | 基于 `beagle - 图鉴系统` 的详案、图鉴任务配置、UI需求和文本需求生成 `数据打点` 页签；参考/CP/反馈仅作为辅助背景，并导出 xlsx 复查标题、行高、列宽与样式 |
| 2026-05-15 | 生成功能解锁数据打点需求页签 | 飞书 `ZyVWsEuAAhARJ1tiivXcl1krnUd` / `42FLkk`、`session/session.md` | 基于 `Beagle - 功能解锁` 的详案、功能解锁 list、UI需求和文本需求生成 `数据打点` 页签；隐藏 FTE 讨论与功能 List 仅用于核对范围，并导出 xlsx 复查标题、行高、列宽与样式 |
| 2026-05-15 | 生成支线任务数据打点需求页签 | 飞书 `Lt7nsXG2IhhPx1tRQf4cuflSnac` / `om1Ww`、`session/session.md` | 基于 `beagle - 支线任务` 的总览、详案、UI需求和文本需求生成 `数据打点` 页签；参考页签仅作背景，并导出 xlsx 复查标题、行高、列宽与样式 |
| 2026-05-15 | 生成设置界面数据打点需求页签 | 飞书 `NWtVs3TnQh7uCotFnXrcXyZFnwd` / `15ujTy`、`session/session.md` | 基于 `设置界面` 的详细方案、方案和外部 push 页签生成 `数据打点` 页签；界面参考仅作背景，并导出 xlsx 复查标题、行高、列宽与样式 |
| 2026-05-15 | 优化数据打点明细表结构规则 | `.cursor/skills/planning-analytics-tracking/SKILL.md`、`.cursor/skills/planning-analytics-tracking/reference.md`、`session/session.md` | 保持 `## 需求描述总览` 不变；对设置项、开关、滑条、多档选择、功能列表和 push 类型优先输出 `change_type / content_key / 中文分类 / 备注 / UI类型` 轻量映射表，复杂玩法事件才使用字段块 |
| 2026-05-15 | 覆盖设置界面数据打点为轻量结构 | 飞书 `NWtVs3TnQh7uCotFnXrcXyZFnwd` / `15ujTy`、`session/session.md` | 按数据组反馈覆盖原 `数据打点` 页签内容，保留 `## 需求描述总览`，将明细改为 `settingchange`、`settingaction`、`settingpush` 轻量映射表，并导出 xlsx 复查旧冗余列已清空 |
| 2026-05-15 | 生成 CBT 触发教程数据打点需求页签 | 飞书 `AH9QsCTgyh5ByitivhVc6V4Rnod` / `2Nk9I4`、`session/session.md` | 基于 `beagle - CBT 触发教程需求list` 的 Base 视图导出内容生成 `数据打点` 页签；按新规则使用 `tutorialtrigger`、`tutorialsupport` 轻量映射表，并导出 xlsx 复查标题、表头和样式 |
| 2026-05-15 | 修正数据打点结构判断规则 | `.cursor/skills/planning-analytics-tracking/SKILL.md`、`.cursor/skills/planning-analytics-tracking/reference.md`、`session/session.md` | 参考 `比格 数据埋点设计` 的客户端/服务器设计页、`FTE步骤`、`settingchange`、`uiclick` 等结构，将规则改为先判断上报端、承接表、记录粒度和明细结构，再决定输出事件字段块、枚举维表或两者组合，避免硬套轻量映射表 |
| 2026-05-18 | 生成联盟音频需求页签 | 飞书 `B6B4sUCt7hV4qktXqGacaiYqnCb` / `3Z0Mwg`、`session/session.md` | 基于 `详细方案`、联盟界面包装方案和联盟礼物包装生成 `音频需求` 页签；包含策划必看、音乐需求、6 个音效交互块与待确认事项，并导出 xlsx 复查标题、行高和合并区域 |
| 2026-05-19 | 生成表情系统音频需求页签并试加切图字段 | 飞书 `A6SwsrrhjhoWgrtSBbQcs8LAnGf` / `1OPsSk`、`session/session.md` | 基于 `详细方案`、`表情汇总`、`文本需求`、`配置结构` 生成 `音频需求` 页签；按音频反馈在每个音效细分项新增 `对应切图` 行，引用详细方案图片所在行；飞书图片写入 API 返回 `95201 server error`，本轮先保留文字定位引用 |
| 2026-05-19 | 固化音频需求对应切图规则 | `.cursor/skills/planning-audio-requirements/SKILL.md`、`session/session.md` | 根据音频同学反馈，将 `对应切图` 纳入音乐/音效细分需求固定字段；优先引用详细方案已有图片，无法复制图片实体时保留来源页签、行号/单元格和画面摘要 |
| 2026-05-19 | 优化音频需求切图显示样式 | 飞书 `A6SwsrrhjhoWgrtSBbQcs8LAnGf` / `1OPsSk`、`.cursor/skills/planning-audio-requirements/SKILL.md`、`session/session.md` | 使用表格浮动图片接口把详细方案已有图片直接显示到 `对应切图` 行；清空切图来源文字和 `策划补充提示` 行，并将规则改为有图时不再输出策划补充提示 |
| 2026-05-19 | 修正音效需求报错反馈口径 | 飞书 `A6SwsrrhjhoWgrtSBbQcs8LAnGf` / `1OPsSk`、`.cursor/skills/planning-audio-requirements/SKILL.md`、`session/session.md` | 删除表情系统音频需求中的“表情发送失败与错误提示反馈”音效块；规则补充普通报错、发送冷却、内容不存在等轻量 UI 错误反馈不单独拆音效需求 |
| 2026-05-19 | 重写小队系统音频需求页签 | 飞书 `PwD6siU0HhfVyvtD48mczKZSnJb` / `2caZoc`、`session/session.md` | 按最新音频规则原地重写 `音频需求` 页签；音乐/音效细分项增加直接显示的 `对应切图` 浮动图片，删除 `策划补充提示`，并避免普通反馈文本/报错单独拆音效需求 |
| 2026-05-19 | 收紧音频需求切图来源规则 | 飞书 `PwD6siU0HhfVyvtD48mczKZSnJb` / `2caZoc`、`.cursor/skills/planning-audio-requirements/SKILL.md`、`session/session.md` | 按反馈将默认切图来源收紧为仅使用 `详细方案` 图片；未特殊说明或未单独提供图片时不再取其他页签图片，并替换小队音频需求中来自非详细方案的切图 |
| 2026-05-19 | 增加音频需求登记 Base 流程 | 飞书 Base `AZHgbHFazaDLLBs50cJcoJhKnMf` / `tblfT7sBWJXgRqXY`、`.cursor/skills/planning-audio-requirements/SKILL.md`、`session/session.md` | 生成并写回音频需求后，若用户指定统一登记 Base，需要新增登记记录并只填写策划案链接、需求任务名和对应操作者策划名字；已为小队音频需求新增测试记录 `recvk4jHYYxbp4` |
| 2026-05-19 | 固化音频需求 Base 登记 SOP | `.cursor/skills/planning-audio-requirements/SKILL.md`、`session/session.md` | 将已跑通的 Base 登记流程写入 Skill：包含 7 日版本登记表 token/表 ID/视图 ID、字段映射、最小权限、人员字段 open_id 规则，以及 Windows 下用 Python 传 JSON 的写入方式 |
| 2026-05-19 | 调整音频需求 Base 登记为二次确认 | `.cursor/skills/planning-audio-requirements/SKILL.md`、`session/session.md` | 将需求管理表登记从生成后同步写入改为生成完成后先询问用户是否需要添加；仅在用户二次确认后才写入 Base，未确认时不新增记录 |
| 2026-05-19 | 重新生成联盟音频需求页签 | 飞书 `B6B4sUCt7hV4qktXqGacaiYqnCb` / `3Z0Mwg`、`session/session.md` | 按最新音频规则重写联盟 `音频需求` 页签；为 1 个音乐需求和 6 个音效需求补充详细方案来源的对应切图，移除 `策划补充提示`，并导出 xlsx 复查 7 张图片、行高和分区结构 |
| 2026-05-20 | 修正联盟数据打点需求页签 | 飞书 `B6B4sUCt7hV4qktXqGacaiYqnCb` / `lpViU`、`session/session.md` | 移除误写入页签的结构选型说明，仅保留正式数据打点交付内容；按数据打点页签格式补充合并、标题/分区/表头样式、列宽与行高，并导出 xlsx 复查 |
| 2026-05-21 | 新增公告需求生成 Skill | `.cursor/skills/planning-announcement-requirements/`、`README.md`、`session/session.md` | 固化读取策划详细方案生成玩家版本公告的流程；生成前确认 ROK/COD/Beagle 项目，首版接入 ROK 文案术语库和 ROK 版本公告内容表字段规则 |
| 2026-05-21 | 细化活动类公告生成规则 | `.cursor/skills/planning-announcement-requirements/`、`session/session.md` | 根据付费追赶活动测试反馈，要求活动类公告必须读取背景、参与对象、开放节点、持续时间、参与次数、购买/兑换上限、奖励、商店解锁和限制例外；优化活动需用玩家视角解释为什么要改 |
| 2026-05-21 | 增加规则说明型公告识别规则 | `.cursor/skills/planning-announcement-requirements/`、`session/session.md` | 根据装备冲刺可购买次数文案对比，新增规则说明型公告结构：背景原因、核心规则对象、关键定义、条件分支、计算公式、负向规则、共享/动态规则和移民/赛季限制 |
| 2026-05-21 | 补充活动替代旧活动公告口径 | `.cursor/skills/planning-announcement-requirements/`、`session/session.md` | 根据“中期结算”文案反馈，新增活动若取消或替代旧活动，短版版本公告需优先写清新增活动、开放范围、替代关系、核心得分行为和奖励结算方式，避免展开成规则说明页 |
| 2026-05-21 | 系统读取 ROK 历史公告润色口径 | `.cursor/skills/planning-announcement-requirements/`、`mistakes/announcement-reference-not-read.md`、`session/session.md` | 读取 ROK 版本公告内容表所有页签的润色相关列，修正 Skill 为必须读取 `reference.md`，并在 reference 中沉淀润色列权威优先级、常用句式、先锋体验、规则限制、外观装扮和国服/国际服差异写法 |
| 2026-05-21 | 深读 ROK 1108-1092 公告样本 | `.cursor/skills/planning-announcement-requirements/reference.md`、`session/session.md` | 读取 1108 至 1092 页签 A:G 内容，对比公告内容、备注和润色差异，补充策划口语转公告口径、权限称谓、测试范围、术语纠偏、实际效果边界、版本范围、任务奖励替换和 AI 润色反例规则 |

## 提交总账
- 当前仓库未启用 git，总账先记录在本文件中。
- 若后续接入 git，需将提交记录与本节保持一致，确保文档账本与代码状态可对齐。

## 下一步
1. 补充历史样例表与 key 规则文档，替换默认模板流程。
2. 用高清局部图或拆分图再次测试，验证弹窗正文与中文文案识别质量。
3. 若要继续飞书目录自动化，补齐 `drive:drive` 或 `space:folder:create` 权限后重新授权。
4. 用真实飞书策划案链接验证 `planning-analytics-tracking` 的读取、埋点生成与文档写回。
5. 用真实飞书策划案链接继续验证 `planning-audio-requirements` 的音乐判定边界、音效判定边界、复合功能拆分、配音需求抽取和样式参考说明。
6. 用真实 ROK 策划案验证 `planning-announcement-requirements` 的术语库读取、公告规模判断、代表截图选择和公告内容表写入流程。
