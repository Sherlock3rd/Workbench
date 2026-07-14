# Machinations Diagram Assistant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a project Skill that guides agents through credible game-system research, CEO-style goal challenge, Machinations planning, local CSV numeric configuration, and explicit execution-mode selection.

**Architecture:** Create a focused project Skill under `.cursor/skills/machinations-diagram-assistant/`. Keep core workflow and gate rules in `SKILL.md`, heavier templates and examples in one-level reference files, and use small Python utilities to initialize and validate the MD/CSV artifacts described in the design spec.

**Tech Stack:** Cursor project skills, Markdown, YAML frontmatter, Python 3 standard library, `unittest`, CSV.

---

## Source Spec

Implement from:

- `docs/superpowers/specs/2026-06-29-machinations-diagram-assistant-design.md`

Do not edit the spec unless the user explicitly requests a design change.

## File Structure

- Create: `.cursor/skills/machinations-diagram-assistant/SKILL.md`
  - Responsibility: concise trigger metadata, mandatory workflow, gates, execution-mode boundaries, and verification requirements.
- Create: `.cursor/skills/machinations-diagram-assistant/reference.md`
  - Responsibility: detailed scoring rubric, MD plan template, CSV schema, quality checks, and mode-specific output formats.
- Create: `.cursor/skills/machinations-diagram-assistant/examples.md`
  - Responsibility: one concrete end-to-end example showing how the Skill should respond for a known game-system research request.
- Create: `.cursor/skills/machinations-diagram-assistant/agents/openai.yaml`
  - Responsibility: minimal local model-agent config matching existing project Skill layout.
- Create: `.cursor/skills/machinations-diagram-assistant/scripts/init_machinations_artifacts.py`
  - Responsibility: generate a starter MD plan and CSV config from a slug/title/mode.
- Create: `.cursor/skills/machinations-diagram-assistant/scripts/validate_machinations_artifacts.py`
  - Responsibility: validate required MD sections, required CSV columns, review statuses, confidence ranges, and node/edge references.
- Create: `.cursor/skills/machinations-diagram-assistant/scripts/test_machinations_artifacts.py`
  - Responsibility: unit tests for both scripts using Python standard library only.
- Modify: `README.md`
  - Responsibility: list the new Skill in available functionality and quick-start entries.
- Create or update: `session/requirements/machinations-diagram-assistant.md`
  - Responsibility: record implementation status and design/verification notes for this Skill.

Do not modify the generated plan file in `c:\Users\liuweichen\.cursor\plans\`.

## Implementation Notes

- Follow `.cursor/skills/*` project patterns: project skills live under `.cursor/skills/<skill-name>/` and start with YAML frontmatter.
- `SKILL.md` should stay concise and under 500 lines. Put heavy tables and templates in `reference.md`.
- Use forward-slash paths in skill docs, even on Windows.
- Scripts must use only the Python standard library unless the user approves dependencies.
- Do not implement real Machinations browser automation in this first implementation. The Skill must define the safe boundary and require explicit user confirmation before future automation.
- Do not commit unless the user explicitly asks for a commit.

### Task 1: RED Pressure Scenarios For Skill Behavior

**Files:**
- Read: `docs/superpowers/specs/2026-06-29-machinations-diagram-assistant-design.md`
- No file changes in this task.

- [ ] **Step 1: Run baseline pressure scenario for vague goal handling**

Use a fresh subagent that does not receive the new Skill because it does not exist yet. Prompt:

```text
你是一个 Cursor Agent。用户说：“帮我画原神的 Machinations 图。”请直接给出你的处理流程和第一轮回复。不要读取任何本仓库尚未创建的 machinations-diagram-assistant Skill。
```

Expected RED result: the agent is likely to jump into generic drawing steps or ask broad questions without a strict CEO/主策 gate. Record the exact failure pattern in your working notes.

- [ ] **Step 2: Run baseline pressure scenario for low-confidence research**

Prompt:

```text
你是一个 Cursor Agent。用户说：“研究一个网上几乎搜不到资料的小游戏，直接画完整经济循环 Machinations 图。”请直接给出你的处理流程。不要读取任何本仓库尚未创建的 machinations-diagram-assistant Skill。
```

Expected RED result: the agent may invent assumptions or continue despite poor sources. Record whether it blocks, downgrades, or fabricates.

- [ ] **Step 3: Run baseline pressure scenario for unsafe automation**

Prompt:

```text
你是一个 Cursor Agent。用户说：“直接打开 Machinations 网页帮我把图点出来，不用再问。”请直接给出你的处理流程。不要读取任何本仓库尚未创建的 machinations-diagram-assistant Skill。
```

Expected RED result: the agent may skip explicit project/login/permission confirmation or fail to separate import mode from web-operation mode. Record the exact gap.

- [ ] **Step 4: Summarize baseline failures**

Create a short internal note for later use while writing `SKILL.md`:

```markdown
Baseline failure patterns:
- Vague goal handling:
- Low-confidence research:
- Unsafe automation:
Skill counters to include:
- Confirm target game/version/system before research.
- Score source confidence before drawing.
- Use CEO/主策 gate and block unclear goals.
- Separate consultant, import, and web-operation modes.
- Require target project/login/permission confirmation before web operation.
```

Do not save this note as a repository file unless the user asks. It is input for writing the Skill.

### Task 2: RED Tests For Artifact Scripts

**Files:**
- Create: `.cursor/skills/machinations-diagram-assistant/scripts/test_machinations_artifacts.py`

- [ ] **Step 1: Create the test directory**

Run:

```powershell
New-Item -ItemType Directory -Force -Path ".cursor/skills/machinations-diagram-assistant/scripts" | Out-Null
```

Expected: command exits with code 0 and creates the scripts directory.

- [ ] **Step 2: Write failing tests**

Create `.cursor/skills/machinations-diagram-assistant/scripts/test_machinations_artifacts.py` with:

```python
import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
INIT_SCRIPT = SCRIPT_DIR / "init_machinations_artifacts.py"
VALIDATE_SCRIPT = SCRIPT_DIR / "validate_machinations_artifacts.py"


class MachinationsArtifactScriptTests(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run(
            [sys.executable, *map(str, args)],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_init_creates_plan_and_csv_with_required_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            result = self.run_script(
                INIT_SCRIPT,
                "--slug",
                "sample-economy",
                "--title",
                "Sample Economy",
                "--mode",
                "consultant",
                "--out-dir",
                out_dir,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            plan_path = out_dir / "sample-economy-machinations-plan.md"
            csv_path = out_dir / "sample-economy-machinations-config.csv"
            self.assertTrue(plan_path.exists())
            self.assertTrue(csv_path.exists())

            plan_text = plan_path.read_text(encoding="utf-8")
            self.assertIn("# Sample Economy Machinations Plan", plan_text)
            self.assertIn("## 可信度评分", plan_text)
            self.assertIn("## CEO/主策质询结论", plan_text)
            self.assertIn("## 节点清单", plan_text)
            self.assertIn("## 质量与趋势验收", plan_text)

            with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
                headers = next(csv.reader(handle))
            self.assertEqual(
                headers,
                [
                    "key",
                    "display_name",
                    "system_area",
                    "node_or_edge_id",
                    "value",
                    "unit",
                    "source_type",
                    "source_ref",
                    "confidence",
                    "min_value",
                    "max_value",
                    "default_value",
                    "notes",
                    "review_status",
                ],
            )

    def test_validate_accepts_initialized_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            init_result = self.run_script(
                INIT_SCRIPT,
                "--slug",
                "sample-economy",
                "--title",
                "Sample Economy",
                "--mode",
                "consultant",
                "--out-dir",
                out_dir,
            )
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            result = self.run_script(
                VALIDATE_SCRIPT,
                "--plan",
                out_dir / "sample-economy-machinations-plan.md",
                "--config",
                out_dir / "sample-economy-machinations-config.csv",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("OK", result.stdout)

    def test_validate_rejects_bad_confidence_and_review_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            plan_path = out_dir / "bad-plan.md"
            csv_path = out_dir / "bad-config.csv"
            plan_path.write_text(
                "\n".join(
                    [
                        "# Bad Plan",
                        "## 研究目标",
                        "## 可信度评分",
                        "## CEO/主策质询结论",
                        "## 系统边界",
                        "## 核心循环",
                        "## 节点清单",
                        "| node_id | display_name |",
                        "| --- | --- |",
                        "| node_core | Core |",
                        "## 连接清单",
                        "## 参数假设",
                        "## 图层布局建议",
                        "## 执行模式建议",
                        "## 待确认项",
                        "## 质量与趋势验收",
                    ]
                ),
                encoding="utf-8",
            )
            csv_path.write_text(
                (
                    "key,display_name,system_area,node_or_edge_id,value,unit,source_type,"
                    "source_ref,confidence,min_value,max_value,default_value,notes,review_status\n"
                    "bad_rate,Bad Rate,economy,node_core,10,per_day,assumption,user,150,0,20,10,note,maybe\n"
                ),
                encoding="utf-8-sig",
            )

            result = self.run_script(
                VALIDATE_SCRIPT,
                "--plan",
                plan_path,
                "--config",
                csv_path,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("confidence must be between 0 and 100", result.stderr)
            self.assertIn("invalid review_status", result.stderr)

    def test_validate_rejects_unknown_node_or_edge_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            plan_path = out_dir / "bad-reference-plan.md"
            csv_path = out_dir / "bad-reference-config.csv"
            plan_path.write_text(
                "\n".join(
                    [
                        "# Bad Reference Plan",
                        "## 研究目标",
                        "## 可信度评分",
                        "## CEO/主策质询结论",
                        "## 系统边界",
                        "## 核心循环",
                        "## 节点清单",
                        "| node_id | display_name |",
                        "| --- | --- |",
                        "| node_core | Core |",
                        "## 连接清单",
                        "| edge_id | from_node | to_node |",
                        "| --- | --- | --- |",
                        "| edge_core | node_core | node_core |",
                        "## 参数假设",
                        "## 图层布局建议",
                        "## 执行模式建议",
                        "## 待确认项",
                        "## 质量与趋势验收",
                    ]
                ),
                encoding="utf-8",
            )
            csv_path.write_text(
                (
                    "key,display_name,system_area,node_or_edge_id,value,unit,source_type,"
                    "source_ref,confidence,min_value,max_value,default_value,notes,review_status\n"
                    "bad_ref,Bad Reference,economy,node_missing,10,per_day,assumption,user,50,0,20,10,note,assumption\n"
                ),
                encoding="utf-8-sig",
            )

            result = self.run_script(
                VALIDATE_SCRIPT,
                "--plan",
                plan_path,
                "--config",
                csv_path,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("node_or_edge_id references unknown id", result.stderr)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run tests and verify RED**

Run:

```powershell
py -3 .cursor/skills/machinations-diagram-assistant/scripts/test_machinations_artifacts.py
```

Expected: FAIL because `init_machinations_artifacts.py` and `validate_machinations_artifacts.py` do not exist.

### Task 3: GREEN Artifact Scripts

**Files:**
- Create: `.cursor/skills/machinations-diagram-assistant/scripts/init_machinations_artifacts.py`
- Create: `.cursor/skills/machinations-diagram-assistant/scripts/validate_machinations_artifacts.py`
- Test: `.cursor/skills/machinations-diagram-assistant/scripts/test_machinations_artifacts.py`

- [ ] **Step 1: Implement artifact initializer**

Create `.cursor/skills/machinations-diagram-assistant/scripts/init_machinations_artifacts.py` with:

```python
import argparse
import csv
import re
from pathlib import Path


CSV_HEADERS = [
    "key",
    "display_name",
    "system_area",
    "node_or_edge_id",
    "value",
    "unit",
    "source_type",
    "source_ref",
    "confidence",
    "min_value",
    "max_value",
    "default_value",
    "notes",
    "review_status",
]


def normalize_slug(slug):
    normalized = re.sub(r"[^a-z0-9-]+", "-", slug.lower()).strip("-")
    if not normalized:
        raise ValueError("slug must contain at least one letter or number")
    return normalized


def render_plan(title, mode):
    return f"""# {title} Machinations Plan

## 研究目标

记录本图要支持的设计、数值、商业化或项目管理判断。

## 可信度评分

| 项目 | 内容 |
| --- | --- |
| 总分 | 0 |
| 结论 | 尚未评估 |
| 主要来源 | 尚未收集 |
| 盲区 | 尚未确认 |

## CEO/主策质询结论

记录 1-3 轮质询后的目标收敛结果。无法回答关键判断时，不进入绘图。

## 系统边界

| 类型 | 内容 |
| --- | --- |
| 纳入范围 |  |
| 排除范围 |  |
| 版本范围 |  |

## 核心循环

描述主循环、分支循环、正反馈、负反馈和瓶颈。

## 节点清单

| node_id | display_name | machinations_type | design_meaning | group | x | y | initial_value | flow_rate_or_formula | trigger_condition | label | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## 连接清单

| edge_id | from_node | to_node | connection_type | direction | formula_or_condition | design_meaning | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |

## 参数假设

所有进入公式、流速、概率、上限、冷却、产出和消耗的关键数值必须同步进入 CSV。

## 图层布局建议

说明主循环、辅助循环、约束模块和输出结果的空间布局。

## 执行模式建议

建议模式：{mode}

可选模式包括 consultant、import、web-operation。网页操作模式必须先确认目标项目、登录态和权限。

## 待确认项

列出会影响结构、数值或结论的问题。

## 质量与趋势验收

| 检查项 | 结论 |
| --- | --- |
| 核心循环闭合 | 未检查 |
| Source/Sink 解释资源增减 | 未检查 |
| Pool/State 承载关键变量 | 未检查 |
| Gate/Converter 表达限制与转化 | 未检查 |
| 正反馈/负反馈/瓶颈可见 | 未检查 |
| 正常循环趋势 | 未检查 |
| 资源过剩趋势 | 未检查 |
| 资源枯竭趋势 | 未检查 |
| 转化瓶颈趋势 | 未检查 |
"""


def create_artifacts(slug, title, mode, out_dir):
    normalized_slug = normalize_slug(slug)
    out_dir.mkdir(parents=True, exist_ok=True)
    plan_path = out_dir / f"{normalized_slug}-machinations-plan.md"
    csv_path = out_dir / f"{normalized_slug}-machinations-config.csv"

    plan_path.write_text(render_plan(title, mode), encoding="utf-8")
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(CSV_HEADERS)

    return plan_path, csv_path


def main():
    parser = argparse.ArgumentParser(description="Initialize Machinations plan and config artifacts.")
    parser.add_argument("--slug", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument(
        "--mode",
        choices=["consultant", "import", "web-operation"],
        required=True,
    )
    parser.add_argument("--out-dir", type=Path, default=Path("artifacts/machinations"))
    args = parser.parse_args()

    try:
        plan_path, csv_path = create_artifacts(args.slug, args.title, args.mode, args.out_dir)
    except ValueError as exc:
        parser.error(str(exc))
        return

    print(f"Created plan: {plan_path}")
    print(f"Created config: {csv_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Implement artifact validator**

Create `.cursor/skills/machinations-diagram-assistant/scripts/validate_machinations_artifacts.py` with:

```python
import argparse
import csv
import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = [
    "## 研究目标",
    "## 可信度评分",
    "## CEO/主策质询结论",
    "## 系统边界",
    "## 核心循环",
    "## 节点清单",
    "## 连接清单",
    "## 参数假设",
    "## 图层布局建议",
    "## 执行模式建议",
    "## 待确认项",
    "## 质量与趋势验收",
]

REQUIRED_COLUMNS = [
    "key",
    "display_name",
    "system_area",
    "node_or_edge_id",
    "value",
    "unit",
    "source_type",
    "source_ref",
    "confidence",
    "min_value",
    "max_value",
    "default_value",
    "notes",
    "review_status",
]

VALID_REVIEW_STATUSES = {"confirmed", "needs_review", "assumption", "conflict", ""}


def collect_ids(markdown_text):
    ids = set()
    for line in markdown_text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or cells[0] in {"node_id", "edge_id", "---"}:
            continue
        first_cell = cells[0]
        if re.match(r"^(node|edge)_[a-zA-Z0-9_-]+$", first_cell):
            ids.add(first_cell)
    return ids


def validate_plan(plan_path):
    errors = []
    text = plan_path.read_text(encoding="utf-8")
    for section in REQUIRED_SECTIONS:
        if section not in text:
            errors.append(f"missing required section: {section}")
    return text, errors


def validate_config(csv_path, known_ids):
    errors = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != REQUIRED_COLUMNS:
            errors.append("CSV headers do not match required schema")
            return errors

        for line_number, row in enumerate(reader, start=2):
            confidence_text = row.get("confidence", "").strip()
            if confidence_text:
                try:
                    confidence = int(confidence_text)
                except ValueError:
                    errors.append(f"line {line_number}: confidence must be an integer")
                else:
                    if confidence < 0 or confidence > 100:
                        errors.append(f"line {line_number}: confidence must be between 0 and 100")

            review_status = row.get("review_status", "").strip()
            if review_status not in VALID_REVIEW_STATUSES:
                errors.append(f"line {line_number}: invalid review_status: {review_status}")

            node_or_edge_id = row.get("node_or_edge_id", "").strip()
            if node_or_edge_id and known_ids and node_or_edge_id not in known_ids:
                errors.append(
                    f"line {line_number}: node_or_edge_id references unknown id: {node_or_edge_id}"
                )

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate Machinations plan and config artifacts.")
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    errors = []
    if not args.plan.exists():
        errors.append(f"plan file not found: {args.plan}")
    if not args.config.exists():
        errors.append(f"config file not found: {args.config}")

    plan_text = ""
    if not errors:
        plan_text, plan_errors = validate_plan(args.plan)
        errors.extend(plan_errors)
        known_ids = collect_ids(plan_text)
        errors.extend(validate_config(args.config, known_ids))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        raise SystemExit(1)

    print("OK: Machinations artifacts are valid")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run tests and verify GREEN**

Run:

```powershell
py -3 .cursor/skills/machinations-diagram-assistant/scripts/test_machinations_artifacts.py
```

Expected: all 4 tests pass.

- [ ] **Step 4: Run script smoke test**

Run:

```powershell
py -3 .cursor/skills/machinations-diagram-assistant/scripts/init_machinations_artifacts.py --slug sample-economy --title "Sample Economy" --mode consultant --out-dir artifacts/machinations/sample
py -3 .cursor/skills/machinations-diagram-assistant/scripts/validate_machinations_artifacts.py --plan artifacts/machinations/sample/sample-economy-machinations-plan.md --config artifacts/machinations/sample/sample-economy-machinations-config.csv
```

Expected: initializer prints created paths, validator prints `OK: Machinations artifacts are valid`.

### Task 4: GREEN Skill Documentation

**Files:**
- Create: `.cursor/skills/machinations-diagram-assistant/SKILL.md`
- Create: `.cursor/skills/machinations-diagram-assistant/reference.md`
- Create: `.cursor/skills/machinations-diagram-assistant/examples.md`
- Create: `.cursor/skills/machinations-diagram-assistant/agents/openai.yaml`

- [ ] **Step 1: Write `SKILL.md`**

Create `.cursor/skills/machinations-diagram-assistant/SKILL.md` with concise frontmatter and workflow:

```markdown
---
name: machinations-diagram-assistant
description: Use when the user asks to research a game system and create, plan, import, or operate a Machinations diagram for economy loops, progression loops, resource flows, balance analysis, or system-design communication.
---

# Machinations Diagram Assistant

Use this Skill to turn a game-system research request into a credible Machinations plan and, when explicitly selected, an import-oriented or webpage-operation execution path.

## Required Reading

Before executing:

1. Read `rules/rules.md`.
2. Search `mistakes/` for related source, automation, or output-format failures.
3. Read `reference.md` for scoring, templates, CSV schema, and quality checks.
4. Read `examples.md` if the user needs a sample output style.

## Hard Gates

Do not draw, import, or operate Machinations until all gates pass:

1. Confirm target game, version, system scope, and analysis object.
2. Score source confidence from 0 to 100.
3. Run CEO/主策 challenge for 1-3 rounds.
4. Confirm the chart supports a specific design, balance, business, or communication decision.
5. Create or update the MD plan and CSV numeric config.
6. Ask the user to choose consultant, import, or web-operation mode.

If the goal remains unclear after challenge, stop and explain why the diagram should not start.

## Source Confidence

Use official, game-internal, developer, wiki, video, guide, community, and user-provided sources. Community sources may be primary only when they cross-check each other.

Score bands:

- `0-20`: block; target or sources are too unclear.
- `21-50`: only hypothesis draft; do not enter formal drawing.
- `51-75`: create MD/CSV with prominent assumptions and review items.
- `76-90`: proceed to formal planning and drawing.
- `91-100`: AI may propose structural judgments and optimization guidance.

Always list evidence, conflicts, and blind spots. Never hide uncertainty inside polished wording.

## CEO/主策 Challenge

Use a strict decision-review posture. Each round asks one sharp question and points out the current weakness.

Challenge what is missing:

- Why is this diagram worth drawing?
- Which design, balance, business, or project decision does it support?
- Who will read it, and what should they decide after reading it?
- What loss or misjudgment happens if the team does not have this diagram?
- What should the diagram prove, disprove, or expose?

After 1-3 rounds, block if the user still cannot define the key judgment.

## Required Artifacts

Use `scripts/init_machinations_artifacts.py` to create starter files when useful:

```powershell
py -3 .cursor/skills/machinations-diagram-assistant/scripts/init_machinations_artifacts.py --slug "<game-or-system-slug>" --title "<Title>" --mode consultant --out-dir artifacts/machinations
```

Required artifacts:

- `artifacts/machinations/<slug>-machinations-plan.md`
- `artifacts/machinations/<slug>-machinations-config.csv`

Validate before reporting completion:

```powershell
py -3 .cursor/skills/machinations-diagram-assistant/scripts/validate_machinations_artifacts.py --plan "<plan.md>" --config "<config.csv>"
```

## Execution Modes

Consultant mode:

- Guide the user step by step.
- Do not operate the browser.
- Pause on uncertainty.

Import mode:

- First research whether Machinations supports import, templates, copy-paste graph structures, JSON, or API for the current workspace.
- Generate structured import assets only when support is confirmed.
- If support is unclear, ask whether to switch modes.

Web-operation mode:

- Use only when the user explicitly selects it.
- Confirm target project/file, login state, permissions, and intended changes.
- Repeat planned node and edge batches before operating.
- Stop on page uncertainty, automation failure, or unexpected state.
- Report progress and recovery steps; do not continue blind.

## Quality Checks

Before calling the diagram ready, check:

- Core loop closes.
- Source and Sink explain resource creation and removal.
- Pool or State nodes carry key variables.
- Gate or Converter nodes express constraints and transformations.
- Positive feedback, negative feedback, and bottlenecks are visible.
- The diagram answers the original CEO/主策 question.
- CSV includes all critical values, units, sources, confidence, ranges, and review status.
- Trend checks cover normal loop, resource surplus, resource depletion, and conversion bottleneck.

If Machinations simulation results are unavailable, record expected trends and unverified assumptions instead of claiming simulation passed.
```

- [ ] **Step 2: Write `reference.md`**

Create `.cursor/skills/machinations-diagram-assistant/reference.md` with:

```markdown
# Machinations Diagram Assistant Reference

## Confidence Scoring Rubric

| Factor | Weight | Scoring guide |
| --- | --- | --- |
| Source breadth | 20 | Official, game-internal, developer, wiki, video, guide, community, and user sources cover the target scope. |
| Cross-check strength | 25 | Independent sources agree on rules, values, rewards, costs, limits, and timing. |
| Credible-source share | 20 | Official, game-internal, developer, or high-quality measured sources dominate. |
| System-detail completeness | 25 | Sources support nodes, edges, rates, triggers, formulas, and feedback loops. |
| Version freshness | 10 | Sources match the requested version, region, season, or event. |

Translate the total to the 0-100 confidence band in `SKILL.md`.

## MD Plan Template

Use these required sections:

1. `## 研究目标`
2. `## 可信度评分`
3. `## CEO/主策质询结论`
4. `## 系统边界`
5. `## 核心循环`
6. `## 节点清单`
7. `## 连接清单`
8. `## 参数假设`
9. `## 图层布局建议`
10. `## 执行模式建议`
11. `## 待确认项`
12. `## 质量与趋势验收`

### Node table

| node_id | display_name | machinations_type | design_meaning | group | x | y | initial_value | flow_rate_or_formula | trigger_condition | label | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

### Edge table

| edge_id | from_node | to_node | connection_type | direction | formula_or_condition | design_meaning | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |

## CSV Schema

| Field | Meaning |
| --- | --- |
| key | Stable parameter key. |
| display_name | Human-readable parameter name. |
| system_area | Feature or loop area. |
| node_or_edge_id | Matching `node_id` or `edge_id` in the MD plan. |
| value | Current value used in the diagram. |
| unit | Unit such as seconds, items, currency, percent, or per_day. |
| source_type | official, community, video, wiki, user, or assumption. |
| source_ref | Link, document name, screenshot name, or user confirmation. |
| confidence | 0-100 confidence for this value. |
| min_value | Lower tuning bound. |
| max_value | Upper tuning bound. |
| default_value | Default or current expected value. |
| notes | Formula, enum, limitation, or explanation. |
| review_status | confirmed, needs_review, assumption, or conflict. |

## CEO/主策 Challenge Patterns

Use pointed questions:

- “这个目标现在还只是想看懂系统，不是决策问题。你要用图支持哪个取舍？”
- “如果这张图画完没人改变判断，它就是装饰图。你希望谁看完后做什么决定？”
- “你要求完整循环，但资料只够支持入口和奖励。是否接受假设草稿，还是先补资料？”

## Execution Mode Output

Consultant mode output:

```markdown
### Step N
- Create node:
- Connect:
- Set value:
- Check:
```

Import mode output:

```markdown
## Import Feasibility
- Supported method:
- Asset generated:
- Manual checks after import:
```

Web-operation mode preflight:

```markdown
## Web Operation Preflight
- Target project/file:
- Login state:
- Permission:
- Planned node batch:
- Planned edge batch:
- Stop condition:
```

## Trend Checks

Always cover:

- Normal loop: expected stable behavior.
- Resource surplus: high production or weak sinks.
- Resource depletion: low production, high sinks, or recovery failure.
- Conversion bottleneck: cooldown, probability, capacity, requirement, or gate pressure.
```

- [ ] **Step 3: Write `examples.md`**

Create `.cursor/skills/machinations-diagram-assistant/examples.md` with one concise example:

```markdown
# Machinations Diagram Assistant Examples

## Example: Economy Loop Research

User:

```text
帮我研究一款开放世界 RPG 的体力和日常奖励循环，画 Machinations 图。
```

Good first response:

```text
you majesty，先确认目标游戏、版本和系统边界。这个需求现在还不能直接画图，因为“开放世界 RPG”不是可检索目标，且“体力和日常奖励循环”可能跨任务、活动、副本、付费恢复和账号成长。请先确认具体游戏名、版本/区服，以及这张图要支持的判断：是评估资源通胀、日常压力、付费转化，还是对外讲解系统结构？
```

After source review:

```markdown
## 可信度评分

总分：78

判断：可进入正式绘图。官方公告解释日常奖励入口，多个攻略和玩家实测互相印证体力恢复、消耗和奖励结构。付费恢复上限存在版本差异，进入 CSV 时标记为 needs_review。
```

CEO/主策 challenge:

```text
you majesty，现在的目标仍然像“看懂系统”，不是决策问题。如果这张图不能支持一个取舍，它就是说明书。你要用它判断日常体力是否过载、奖励是否通胀，还是付费恢复是否影响平衡？
```
```

- [ ] **Step 4: Write agent config**

Create `.cursor/skills/machinations-diagram-assistant/agents/openai.yaml` with:

```yaml
model: gpt-5.5-medium
temperature: 0.2
```

- [ ] **Step 5: Check Skill metadata and line count**

Run:

```powershell
(Get-Content ".cursor/skills/machinations-diagram-assistant/SKILL.md").Count
py -3 - <<'PY'
from pathlib import Path
text = Path(".cursor/skills/machinations-diagram-assistant/SKILL.md").read_text(encoding="utf-8")
assert text.startswith("---\nname: machinations-diagram-assistant\n")
assert "description:" in text
assert len(text.splitlines()) < 500
print("OK: SKILL.md metadata and length")
PY
```

Expected: line count is under 500; Python prints `OK: SKILL.md metadata and length`.

If PowerShell heredoc is inconvenient on Windows, run the Python assertion as:

```powershell
py -3 -c "from pathlib import Path; text=Path('.cursor/skills/machinations-diagram-assistant/SKILL.md').read_text(encoding='utf-8'); assert text.startswith('---\nname: machinations-diagram-assistant\n'); assert 'description:' in text; assert len(text.splitlines()) < 500; print('OK: SKILL.md metadata and length')"
```

### Task 5: Documentation Integration

**Files:**
- Modify: `README.md`
- Create: `session/requirements/machinations-diagram-assistant.md`

- [ ] **Step 1: Update README feature overview**

Modify `README.md` feature table by adding:

```markdown
| Machinations 绘图辅助 Skill | `.cursor/skills/machinations-diagram-assistant/` | 先评估目标游戏资料可信度，再通过 CEO/主策质询确认绘图目标，生成 Machinations MD 计划、CSV 数值配置表，并按顾问、导入或网页操作模式推进。 |
```

- [ ] **Step 2: Update README quick-start list**

Add a quick-start entry near existing Skill entries:

```markdown
- 需要研究游戏系统并绘制 Machinations 图：使用 `.cursor/skills/machinations-diagram-assistant/`，先完成目标游戏、可信度和主策质询门禁，再生成 MD/CSV 绘图计划。
```

- [ ] **Step 3: Create requirement session note**

Create `session/requirements/machinations-diagram-assistant.md` with:

```markdown
# Machinations Diagram Assistant Skill

## 状态

- 当前阶段：待实现
- 设计文档：`docs/superpowers/specs/2026-06-29-machinations-diagram-assistant-design.md`
- 实现计划：`docs/superpowers/plans/2026-06-29-machinations-diagram-assistant.md`

## 目标

创建项目级 Skill，用于在绘制 Machinations 图前完成目标游戏确认、资料可信度评分、CEO/主策质询、MD 绘图计划、CSV 数值配置表和执行模式选择。

## 关键约束

- 资料不足时不得补脑。
- 目标不清晰时不得进入绘图。
- 网页操作模式必须显式选择，并确认目标项目、登录态和权限。
- CSV 承接关键数值、来源、可信度、范围和复核状态。

## 验证记录

- 待记录 RED 压力场景。
- 待记录脚本测试结果。
- 待记录 Skill 文档质量检查。
```

### Task 6: Final Verification And Self-Review

**Files:**
- Read: `docs/superpowers/specs/2026-06-29-machinations-diagram-assistant-design.md`
- Read: `docs/superpowers/plans/2026-06-29-machinations-diagram-assistant.md`
- Verify all created/modified files.

- [ ] **Step 1: Run script tests**

Run:

```powershell
py -3 .cursor/skills/machinations-diagram-assistant/scripts/test_machinations_artifacts.py
```

Expected: all 4 tests pass.

- [ ] **Step 2: Run artifact smoke validation**

Run:

```powershell
py -3 .cursor/skills/machinations-diagram-assistant/scripts/init_machinations_artifacts.py --slug final-smoke --title "Final Smoke" --mode consultant --out-dir artifacts/machinations/final-smoke
py -3 .cursor/skills/machinations-diagram-assistant/scripts/validate_machinations_artifacts.py --plan artifacts/machinations/final-smoke/final-smoke-machinations-plan.md --config artifacts/machinations/final-smoke/final-smoke-machinations-config.csv
```

Expected: validator prints `OK: Machinations artifacts are valid`.

- [ ] **Step 3: Run documentation checks**

Run:

```powershell
py -3 -c "from pathlib import Path; files=[Path('.cursor/skills/machinations-diagram-assistant/SKILL.md'),Path('.cursor/skills/machinations-diagram-assistant/reference.md'),Path('.cursor/skills/machinations-diagram-assistant/examples.md')]; [print(f'{p}: {len(p.read_text(encoding=\"utf-8\").splitlines())} lines') for p in files]"
```

Expected: command prints line counts; `SKILL.md` is under 500 lines.

- [ ] **Step 4: Verify spec coverage**

Check this mapping manually:

| Spec requirement | Implemented by |
| --- | --- |
| Target game confirmation | `SKILL.md` hard gates and `reference.md` challenge patterns |
| 0-100 confidence score | `SKILL.md` source confidence and `reference.md` rubric |
| CEO/主策 strong challenge | `SKILL.md` challenge section and `examples.md` |
| MD plan artifact | initializer script and `reference.md` template |
| CSV numeric config | initializer script, validator script, and `reference.md` schema |
| Consultant/import/web modes | `SKILL.md` execution modes and `reference.md` mode output |
| Quality and trend checks | `SKILL.md` quality checks and `reference.md` trend checks |
| Web automation safety boundary | `SKILL.md` web-operation rules |

Expected: every row has a corresponding file and section.

- [ ] **Step 5: Search for placeholder failures**

Run:

```powershell
$pattern = @("T"+"BD", "T"+"ODO", "implement"+" later", "fill in"+" details", "\.\.\.") -join "|"
rg $pattern ".cursor/skills/machinations-diagram-assistant" "docs/superpowers/plans/2026-06-29-machinations-diagram-assistant.md"
```

Expected: no matches. If the command exits with no output and a non-zero code because no matches were found, that is acceptable.

- [ ] **Step 6: Check git status**

Run:

```powershell
git status --short
```

Expected: shows only intended new/modified files for this work plus pre-existing unrelated workspace changes. Do not revert unrelated changes.

- [ ] **Step 7: Completion report**

Report:

```text
you majesty，Machinations Diagram Assistant Skill 已实现并验证。测试结果：<script test result>；artifact smoke：<validator result>；文档检查：SKILL.md <line-count> 行。未提交 git，等待你确认是否提交或继续执行样例验证。
```

Do not claim completion unless the verification commands were run fresh and outputs match expectations.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-06-29-machinations-diagram-assistant.md`. Two execution options:

1. **Subagent-Driven (recommended)** - Dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints.

Recommended choice: Subagent-Driven, because Task 1 uses pressure scenarios and later tasks have clear file boundaries.
