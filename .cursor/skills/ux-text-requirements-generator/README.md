# UX 文本需求 Skill 使用说明

这是一套给 `游戏系统策划 -> 文案策划` 使用的 Cursor Skill。

它的目标不是单纯 OCR，而是把一张 `UX 原型图` 整理成可审阅、可继续编辑的文本需求文档，默认输出为适合飞书/Excel review 的格式。

对外分享时，推荐按 `全引导模式` 使用：
- 同学只需要给出 `UX 原型图文件路径`
- Cursor 自己检查环境
- Cursor 自己安装缺失依赖
- Cursor 自己搜索默认样例表和规则文件
- 如果没有找到，Cursor 自动使用 Skill 内置的默认模板和规则摘要继续处理
- 同学只需要在弹出的确认里点同意或选择即可

默认产出形态：
- 顶部 `UI结构总览`
- 左侧截图
- 中间交互说明
- 右侧 `key / 内容 / 备注`

## 最短使用方式

让外部同学直接在 Cursor 发这句话就可以：

```text
请用 ux-text-requirements-generator 全引导处理这张 UX 图：
D:\你的路径\prototype.png

除了让我点确认和做选择，不要让我手动执行任何命令。
如果缺少 Python 或依赖，请你自己检查并安装。
如果缺少样例表和 key 规则，请直接使用这套 Skill 的默认模板和规则继续。
最后直接给我生成好的 Excel 路径。
```

---

## 1. 这套 Skill 能做什么

适用场景：
- 把长图或拼图式 UX 原型拆成页面章节
- 从页面里提取需要文案支持的文字需求
- 按已有 Excel 模板和 key 规范产出文本需求
- 生成可直接 review 的 `.xlsx` 文件

特别适合：
- 游戏系统界面
- 多状态页面
- 弹窗/抽屉/页签切换
- 需要 `备注` 解释文本位置和作用的需求文档

---

## 2. 第一次使用怎么装

正常情况下，同学 **不需要手动装任何东西**。
推荐直接在 Cursor 里发一句话，让 Skill 自己做环境检查和安装。

推荐直接这样问：

```text
请用 ux-text-requirements-generator 全引导处理这张 UX 图：
D:\你的路径\prototype.png

要求：
1. 你自己检查 Python 和依赖
2. 如果缺环境，直接引导我点确认后帮我安装
3. 如果没有样例表和规则文件，直接用 Skill 内置默认规则继续
4. 最后直接输出 Excel 文件路径给我
```

只有在极少数情况下，如果 Cursor 没有主动执行安装，你才需要手动运行脚本。

### 下面这些命令只作为兜底

正常对外同学不需要执行。
只有在 Cursor 没有自动完成环境检查和安装时，项目管理员才需要手动介入。

### 先检查 Python

在 Windows PowerShell 里运行：

```powershell
py -3 --version
```

如果提示找不到 Python：

```powershell
winget install Python.Python.3.12
```

或者去 [python.org](https://www.python.org/downloads/) 安装 Python 3。

### 一键安装依赖

在仓库根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File ".cursor/skills/ux-text-requirements-generator/scripts/bootstrap_env.ps1"
```

这个脚本会安装：
- `openpyxl`
- `pillow`
- `python-docx`
- `rapidocr-onnxruntime`

### 验证环境是否正常

```powershell
py -3 ".cursor/skills/ux-text-requirements-generator/scripts/extract_sheet_schema.py" "你的案例.xlsx" --sheet "文本键值"
```

如果这条命令能跑通，说明基础环境已经可用。

---

## 3. 需要准备哪些素材

### 对外同学的最低输入

最低只需要 1 个输入：

1. `UX 原型图文件路径`

也就是说，对外同学可以只告诉 Cursor：

```text
请处理这张 UX 图：D:\你的路径\prototype.png
```

然后剩下的事情由 Cursor 引导完成。

### 更完整的输入

如果项目负责人愿意补更多素材，效果会更稳。最推荐准备 3 类输入：

1. `UX 原型图`
- 一张长图、拼图，或者局部高精图都可以
- 如果有高清局部图，尽量一起给

2. `历史文本需求案例`
- 最好是你们已经在飞书/Excel 里实际使用过的表
- 作用是让 Cursor 学会列结构、分章节方式、写法习惯

3. `key 命名规范`
- 比如 key 前缀、模块命名、文本类型后缀、ID 放在哪一段

如果缺样例表或规则文件，也可以先做：
- Cursor 先搜索仓库里的默认文件
- 如果没有找到，则使用 Skill 内置模板和规则摘要
- 输出时标记为 `默认规则推导版`

---

## 4. 建议的工作流程

### 第一步：先让 Cursor 理解结构

不要一上来就让它“直接出最终 Excel”。

先让它做这几件事：
- 识别样例表的列结构
- 识别 key 命名规则
- 识别 UX 图里的章节边界
- 判断每张图是新页面、同页不同状态，还是弹窗/抽屉

### 第二步：先修截图逻辑，再修文本需求

这是整个流程里最关键的一点。

如果截图不对：
- 页面章节会错
- 文本需求会跟图对不上
- 后面再怎么补内容都会越补越偏

所以一定先确认：
- 截图是不是完整页面
- 有没有只截到一半
- 有没有把相邻页面截错
- 有没有把同一 UX 节点错误拆成两章

### 第三步：再逐页补文本需求

正确的提取逻辑不是“把图上所有字都抄一遍”，而是：

- 当前页所有新出现的玩家可见文本
- 当前页相对上一页发生变化的文本
- 标题、按钮、提示、标签、属性名、数值格式
- 需要文案确认的说明文字

对重复不变的基础页文本，不要在每个状态页重复抄一次。

### 第四步：最后生成 Excel

最终用：

```powershell
py -3 "tools/build_ux_requirement_workbook.py" "tools/your_requirement_config.json"
```

---

## 5. Cursor 应该怎么提问

### 最推荐的对外使用方式

让同学只发这一类请求：

```text
请用 ux-text-requirements-generator 全引导处理这张 UX 图：
D:\你的路径\prototype.png
```

然后由 Cursor 主动完成：
- 环境检查
- 依赖安装
- 默认文件搜索
- 章节拆分
- 文本需求生成
- Excel 导出
- 最终路径回传

### 如果你要给同学一句固定话术

可以直接复制这句：

```text
请用 ux-text-requirements-generator 全引导处理这张 UX 图：
D:\你的路径\prototype.png

除了让我点确认和做选择，不要让我手动执行任何命令。
如果缺少 Python 或依赖，请你自己检查并安装。
如果缺少样例表和 key 规则，请直接使用这套 Skill 的默认模板和规则继续。
最后直接给我生成好的 Excel 路径。
```

推荐直接把需求讲完整，至少说清楚这 4 件事：

1. 哪张图是 UX 原型图
2. 如果有的话，哪份文件是历史案例
3. 如果有的话，哪份文件是 key 规则
4. 你想要什么输出

### 推荐提问模板 1：先分析结构

```text
请用 ux-text-requirements-generator 这套 Skill，
先解析 @UX长图.png、@文本需求案例.xlsx、@键值规范.docx。

先不要直接出最终 Excel。
请先完成：
1. 识别案例表的列结构和章节组织方式
2. 识别 key 命名规则
3. 按绿色标题 + 箭头流向 + 同页不同状态，拆分 UX 图章节
4. 告诉我哪些页可能需要高清局部图，哪些页当前裁图有风险
```

### 推荐提问模板 2：开始生成文本需求

```text
请继续用 ux-text-requirements-generator 这套 Skill，
基于 @UX长图.png、@文本需求案例.xlsx、@键值规范.docx，
生成一版可 review 的文本需求。

要求：
1. 先保证截图和章节边界正确
2. 每页只提新增或变化的文本
3. 所有标题、按钮、标签、提示、属性名、数值格式都要判断是否需要提需
4. 输出为左图、中间交互说明、右侧 key/内容/备注 的 Excel
5. 语气用系统策划提给文案策划的写法
```

### 推荐提问模板 3：修错图

```text
请检查当前 Excel 里哪些章节截图和原图对不上。
优先排查：
1. crop_box 是否错了
2. source_image 是否应该换成高清局部图
3. source_coordinate_size 是否和定义坐标时不一致
4. 是否把同一个 UX 节点拆错了

先修截图逻辑，再重新导出。
```

---

## 6. Cursor 在判断“哪些文本要提需求”时，应该怎么想

要用 `UI策划 / 系统策划` 的视角，而不是纯 OCR。

每一页先问 5 个问题：

1. 玩家是通过什么操作来到这一页的？
2. 这一页相对上一页新增了什么 UI？
3. 玩家在这一页新看到、需要理解、需要点击、需要确认的文字是什么？
4. 哪些数字应该写成占位格式，而不是写死具体数值？
5. 哪些文本如果不写 `备注`，文案策划会看不懂它的用途？

通常应该提：
- 页面标题
- 模块标题
- 页签名
- 按钮文案
- 弹窗标题与正文
- 提示语
- 解锁条件
- 警告语
- 属性名称
- 标签名
- 数值展示格式

通常不该提：
- 绿色箭头
- 设计备注
- 裁切辅助线
- 看不清且无法负责推断的碎字
- 上一页已经完整提过、这一页也没有变化的重复文本

---

## 7. 分享给别人时，至少带哪些文件

至少把这些一起发出去：

- `.cursor/skills/ux-text-requirements-generator/README.md`
- `.cursor/skills/ux-text-requirements-generator/SKILL.md`
- `.cursor/skills/ux-text-requirements-generator/reference.md`
- `.cursor/skills/ux-text-requirements-generator/examples.md`
- `.cursor/skills/ux-text-requirements-generator/share-guide.md`
- `.cursor/skills/ux-text-requirements-generator/requirements.txt`
- `.cursor/skills/ux-text-requirements-generator/workbook_config_template.json`
- `.cursor/skills/ux-text-requirements-generator/scripts/bootstrap_env.ps1`
- `.cursor/skills/ux-text-requirements-generator/scripts/*.py`
- `tools/build_ux_requirement_workbook.py`

如果你想让别人一打开就有参考物，建议再带上：

- `tools/pet_growth_requirement_config_v12.json`
- `pet_growth_text_requirements_full_v12.xlsx`

---

## 8. 常见问题

### Q1：为什么 Excel 里的图和原图对不上？

最常见原因：
- `crop_box` 错了
- `source_coordinate_size` 不对
- 原本应该用局部高清图，却被强行映射回主图
- 同一个 UX 节点拆错了章节

结论：先修截图，再修文本。

### Q2：为什么看起来“识别出的文本太少”？

最常见原因不是 OCR 差，而是：
- 章节边界没切对
- 只截到了局部
- 只提了大标题，没提按钮、标签、属性名、提示语和数值格式

### Q3：为什么有些页不应该把所有字都重复提一次？

因为文本需求不是截图抄录，而是“给文案策划的新增/变化需求”。
如果页面只是同页不同状态，应该重点提本状态新出现或变化的文本。

---

## 9. 一句话使用建议

先让 Cursor 帮你“看懂这张 UX 图”，再让它“写文本需求”；先修“截图和章节”，再修“key 和内容”。对外同学只需要给出 UX 图路径，其他步骤都由 Cursor 引导完成。
