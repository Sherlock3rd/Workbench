# Workbench

这是一个面向策划工作流的工具工作台，用于沉淀可复用的 Cursor Skill、飞书集成规范、Agent 执行规则、会话记录和错题复盘。

当前仓库按团队内部分享版整理，目标是让同事 clone 后可以快速了解已有能力，并直接在 Cursor 中复用相关 Skill。

## 可用功能总览

| 模块 | 入口 | 用途 |
| --- | --- | --- |
| 飞书 Agent 部署规范 | `spec/feishu-cli-deployment-and-doc-ops-spec.md` | 记录 Windows 下安装 `@larksuite/cli`、安装 lark skills、初始化配置、用户授权、创建云文档和排查权限问题的完整流程。 |
| 飞书文档写入规范 | `spec/feishu-document-writing-special-flow-spec.md` | 约束所有写回飞书文档和表格的流程，重点解决接口成功但页面缺文本、错位、行高错误、颜色错误等问题。 |
| 本地 Agent 规则规范 | `spec/rules-bootstrap-spec.md` | 在新项目中快速建立“规则、会话、错题、复用”的 Agent 执行体系。 |
| UX 文本需求 Skill | `.cursor/skills/ux-text-requirements-generator/` | 将 UX 原型图整理为可审阅、可继续编辑的文本需求文档，并支持环境检查、依赖安装和 Excel 导出。 |
| 音频需求 Skill | `.cursor/skills/planning-audio-requirements/` | 读取飞书策划案或表格，整理音乐、音效、配音需求，并按音频需求页签样式输出。 |
| 数据打点 Skill | `.cursor/skills/planning-analytics-tracking/` | 读取飞书策划案，先提炼数据问题，再生成事件表、字段和说明，支持写回数据打点区块或页签。 |
| 公告需求 Skill | `.cursor/skills/planning-announcement-requirements/` | 读取飞书策划案或详细方案，确认项目并结合术语库生成面向玩家的版本公告文案；当前已重点支持 ROK，COD/Beagle 仍需补充术语表和训练样本。 |
| 飞书 Sheet 导入 Skill | `.cursor/skills/feishu-sheet-importer/` | 将本地 `.xlsx` 导入飞书 Sheet，并尽量回放章节、表头、配色和图片等关键审阅样式。 |

## 快速开始

1. 克隆仓库：

```powershell
git clone https://github.com/Sherlock3rd/Workbench.git
cd Workbench
```

2. 用 Cursor 打开仓库，先阅读 `rules/rules.md` 了解项目内 Agent 的执行边界。

3. 根据任务选择入口：
   - 需要配置飞书 CLI：阅读 `spec/feishu-cli-deployment-and-doc-ops-spec.md`。
   - 需要写回飞书文档或表格：先阅读 `spec/feishu-document-writing-special-flow-spec.md`。
   - 需要从 UX 图生成文本需求：使用 `.cursor/skills/ux-text-requirements-generator/`。
   - 需要整理音频需求：使用 `.cursor/skills/planning-audio-requirements/`。
   - 需要整理数据打点：使用 `.cursor/skills/planning-analytics-tracking/`。
   - 需要生成版本公告或公告需求：使用 `.cursor/skills/planning-announcement-requirements/`。
   - 需要把本地 Excel 转飞书 Sheet：使用 `.cursor/skills/feishu-sheet-importer/`。

## 目录结构

```text
Workbench/
├── .cursor/skills/        # Cursor Skills，所有可复用能力统一放在这里
├── asset/                 # 内部业务素材和演示资产
├── docs/                  # 术语表、示例文档和补充资料
├── mistakes/              # 错题复盘、踩坑记录和防呆清单
├── rules/                 # 项目级 Agent 规则
├── session/               # 会话总账和需求级会话记录
├── spec/                  # 可复用规范文档
├── tools/                 # 独立脚本或历史工具
└── uxbench/               # UX 工具测试产物和样例输出
```

## 工作方式

1. 开始任务前先读取 `rules/rules.md`，明确确认边界和执行原则。
2. 涉及飞书写入时，先串联飞书 CLI 部署规范和飞书文档写入规范。
3. 具体工具的长期状态记录在 `session/requirements/` 下。
4. 出现可复现错误后，将原因、修复动作和预防办法沉淀到 `mistakes/`。
5. 新增通用规则、规范或 Skill 时，同步更新本 README，保证仓库入口始终可读。

## 内部使用提醒

本仓库当前按团队内部完整版整理，保留了历史会话、业务资料、飞书链接和部分内部配置说明。上传或转发到更公开的范围前，需要重新评估 `session/`、`asset/`、`docs/ROK_*`、飞书 Base token、表 ID、人员 open_id 等内容是否需要脱敏。
