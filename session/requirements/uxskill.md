# `ux-text-requirements-generator` 需求级会话

## 基本信息
- 工具名称：`ux-text-requirements-generator`
- 工具别名：`uxskill`
- 当前状态：已存在工具内容，环境已完成搭建，且已完成首轮测试
- 责任视角：系统策划向文案策划输出可审阅文本需求

## 工具目标
- 将 UX 原型图整理为可继续编辑、可审阅、可导出为 Excel 的文本需求草案。
- 尽量匹配历史样例表结构与 key 命名规则。
- 在缺少样例表或规则文档时，允许使用工具内置模板和默认规则继续推进。

## 当前已知输入
- UX 原型图路径
- 可选历史需求样例表
- 可选 key 命名规则文档

## 当前已知产出
- 结构化文本需求草案
- Excel 可交付文件
- 环境检查与依赖安装引导

## 现状盘点
- 已有 `README.md`、`SKILL.md`、`reference.md`、`examples.md`、`share-guide.md`
- 已有依赖清单 `requirements.txt`
- 已有环境引导脚本 `scripts/bootstrap_env.ps1`
- 已有多个辅助脚本用于 schema 提取、规则提取、原型拆分与行校验

## 环境验证结果
- `py -3 --version`：可用，当前为 Python 3.13.5
- `python --version`：当前仍指向 Python 2.7.18，后续执行命令必须统一使用 `py -3`
- 依赖安装结果：`openpyxl`、`pillow`、`python-docx`、`rapidocr-onnxruntime` 已完成安装
- 导入校验结果：`py -3` 下可成功导入核心依赖

## 风险与待确认
- 若缺少测试用 UX 图、样例表、规则文档，需要决定是否使用默认模板流程。
- 若误用 `python` 命令而非 `py -3`，可能落到 Python 2.7 环境导致脚本失败。
- 大型长图在带绿色箭头和说明字时，自动区域切分容易把整张图识别成一个区域。
- 局部弹窗正文在复杂底图和遮罩场景下可能出现 OCR 语义漂移，需要标记 `待确认`。

## 首轮测试结果
- 测试输入：`uxbench/pic/kvktest.jpg`
- 默认策略：未找到项目样例表与规则文档，改用内置模板和默认 Beagle 规则摘要
- 当前导出链路：使用用户补充的 `.cursor/skills/ux-text-requirements-generator/scripts/build_ux_requirement_workbook.py`
- 中间产物：
  - `uxbench/output/kvktest_workbook_config.json`
  - `uxbench/output/kvktest_requirement_rows.json`
- 最终产物：
  - `uxbench/output/kvktest_ux_text_requirements.xlsx`
- 校验结果：
  - 扁平化 JSON 共 31 行
  - `validate_requirement_rows.py` 校验通过，无缺失列、无重复 key、无正则告警
- 本次新增能力：
  - 新增 `tools/build_ux_requirement_workbook.py`，补足默认模板到 Excel 的导出链路
  - 新增 `.cursor/skills/ux-text-requirements-generator/scripts/build_ux_requirement_workbook.py` 后，已按新脚本要求切换为 `crop_box + crop_name` 配置导出

## 修改记录
| 日期 | 变更 | 说明 |
| --- | --- | --- |
| 2026-04-02 | 初始化需求级会话 | 将 `ux-text-requirements-generator` 纳入项目统一规则与会话体系 |
| 2026-04-02 | 完成环境搭建与依赖校验 | 已安装所需依赖，并确认 `py -3` 可正常导入核心模块 |
| 2026-04-02 | 完成 `kvktest.jpg` 首轮处理 | 已输出 JSON 草案与 Excel 文件，并记录 OCR 与切图风险 |
| 2026-04-02 | 用新版 workbook 脚本重生成 | 已删除上一版输出，改为使用 `.cursor/skills/ux-text-requirements-generator/scripts/build_ux_requirement_workbook.py` 重新导出 |

## 继承指引
- 继承 `rules/rules.md` 中的全部执行原则。
- 设计和命名规则相关变更必须先确认，再修改工具流程。
- 每次测试前先检索 `mistakes/` 中与环境、截图、文本提取相关的记录。

## 下一步
1. 引入历史样例表与 key 规则文档，验证默认 key 命名与真实项目规范的偏差。
2. 对 `kvktest.jpg` 中的弹窗和中文标题做高清局部补图，提升 `待确认` 项的还原度。
3. 若再次测试失败，优先判断是否误用了 `python` 而不是 `py -3`。
