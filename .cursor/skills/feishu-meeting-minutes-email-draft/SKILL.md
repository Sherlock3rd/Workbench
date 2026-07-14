---
name: feishu-meeting-minutes-email-draft
description: "通过会议名关键词和可选模板邮件名自动生成飞书会议纪要邮件草稿：搜索飞书妙记，匹配日历会议，参考指定或默认会议记录模板，创建并保存飞书邮箱草稿，同时在聊天窗口展示邮件内容。适用于用户要求自动生成会议纪要邮件草稿、会议记录邮件、根据会议关键词生成纪要邮件等场景。"
---

# 飞书会议纪要邮件草稿

当用户希望根据会议名关键词自动生成飞书/Lark 邮箱中的会议纪要草稿时，使用本 skill。

## 调用时需要的信息

调用本 skill 时，先要求用户提供两个信息：
- 会议名关键词：必填，用于搜索飞书妙记和匹配日历会议。
- 模板邮件名：可选，用于搜索参考模板邮件；如果用户不提供，则使用本 skill 的默认模板邮件名。

如果会议名关键词缺失，必须先询问用户补充关键词。

如果模板邮件名缺失，不要阻塞流程，使用默认模板：
`【会议记录】组队副本七日版本局内方案讨论`

搜索模板时，必须同时搜索发件箱和收件箱；不要只搜发件箱。

## 默认行为

除非用户另有说明：
- 默认模板邮件名：`【会议记录】组队副本七日版本局内方案讨论`。
- 总结标签：`【ChatGPT5.5 Pro总结】`。
- 收件人：日历中的用户参会人，默认排除当前发件人/本人。
- 抄送：不填写。
- 只创建并保存草稿，绝不直接发送。
- 创建草稿后，必须在聊天窗口展示邮件主题、收件人、无抄送状态、邮件正文内容和草稿链接。

## 依赖能力

按需依次使用这些 skill / CLI 能力：
- `lark-minutes` / `lark-vc`：搜索飞书妙记，获取逐字稿、AI 总结、待办和章节。
- `lark-calendar`：用妙记时间匹配真实日历会议。
- `lark-contact`：当日历参会人缺少邮箱时，将用户 ID 解析为邮箱。
- `lark-mail`：读取模板邮件，并创建/更新邮箱草稿。

使用 `lark-cli` 时优先使用 user 身份。如果遇到 scope/auth 缺失，按 CLI 提示让用户授权，授权后重试。

## 工作流程

1. **收集输入**
   - 明确用户是否提供了：
     - 会议名关键词
     - 模板邮件名
   - 会议名关键词缺失时，询问用户补充。
   - 模板邮件名缺失时，使用默认模板邮件名继续执行，并在内部记录“用户未指定模板，使用默认模板”。

2. **搜索飞书妙记**
   - 按会议名关键词搜索用户自己的妙记，例如：`minutes +search --query "<关键词>" --owner-ids me`。
   - 优先选择标题最匹配、时间最合理、最近的一条。
   - 如果存在多个同样可能的会议，列出简短候选并让用户选择。
   - 获取妙记产物和完整逐字稿。优先使用：`vc +notes --minute-tokens <token> --output-dir <dir> --overwrite`。
   - 记录：妙记标题、token、链接、开始时间、时长、逐字稿路径/内容、AI 总结、待办和章节。

3. **匹配日历会议**
   - 以妙记开始时间为中心搜索日历，通常范围为开始前 90 分钟到开始后 120 分钟。
   - 选择时间最接近且标题/关键词最匹配的日程。
   - 读取日程详情和参会人列表：`calendar events get`、`calendar event.attendees list`。
   - 记录：会议主题、准确开始/结束时间、会议室/地点、主持人/组织者、用户参会人。

4. **解析参会人**
   - 默认收件人为日历中的用户参会人，排除当前发件人/本人。
   - 如缺少邮箱，用 `contact +search-user --user-ids <open_ids> --as user` 解析。
   - 生成正文里的飞书 @ 链接时，优先使用日历 `attendee_id` 的数字部分作为 `data-user-id`，例如 `user_713...` 转为 `713...`。
   - `data-user-id` 是关键字段；缺失时点击 @ 人名会变成写邮件小窗，而不是飞书头像/个人信息卡片。

5. **读取模板邮件**
   - 使用用户提供的模板邮件名；如果未提供，使用默认模板邮件名。
   - 必须同时搜索发件箱和收件箱。
   - 推荐搜索顺序：
     - 先在发件箱按主题精确/模糊搜索。
     - 再在收件箱按主题精确/模糊搜索。
     - 如果 CLI 支持全邮箱搜索，也可以在全邮箱中补充搜索，但不能省略发件箱和收件箱。
   - 如果发件箱和收件箱都找到候选，优先使用标题最匹配、内容最像会议记录模板的一封；如无法判断，列出候选让用户选择。
   - 获取模板邮件完整 `body_html`，参考其视觉结构和富文本写法。
   - 必须保留以下格式特征：
     - 一级标题：蓝色、26px。
     - 二级/三级标题：22px / 20px，加粗。
     - 总结标签：黄色底色，文字为 `【ChatGPT5.5 Pro总结】`。
     - 会议内容条目：条目前缀加粗、正文正常，例如 `<b>玩法定位与参数：</b>正文内容`。
     - 用户 @：使用带 `data-user-id` 的 `<a>`，不是普通邮件链接。
     - 飞书文档链接：使用带 `data-doclink="true"` 和 `mention-type_3` 的 doclink mention 结构，不是普通 URL 链接。

6. **生成邮件正文**
   - 按模板填充以下模块：
     - `会议信息`：会议主题、会议时间、会议地点、主持人、参会人员、方案文档、飞书妙计/妙记链接。
     - `会议内容`：`一、会议议题`、`二、会议结论`。
     - `后续工作安排`。
   - 内容要精简、逐条整理，并忠实于妙记逐字稿和产物。
   - 推荐规模：3-5 条会议议题、2-4 组会议结论、2-4 条后续安排。

7. **创建草稿**
   - 准备好主题、收件人和最终 HTML 后，使用随 skill 附带的脚本创建草稿：
     ```powershell
     node C:\Users\sunqihao\.codex\skills\feishu-meeting-minutes-email-draft\scripts\create_meeting_minutes_draft.js .\payload.json
     ```
   - payload JSON 至少包含：
     ```json
     {
       "subject": "【会议记录】会议主题",
       "to": ["user@example.com"],
       "html": "<div>...</div>"
     }
     ```
   - 脚本会先用 `mail +send` 创建草稿，再用 raw EML 更新同一草稿，以保留 `data-user-id`、`data-doclink` 等飞书富文本属性。

8. **回复用户**
   - 明确说明草稿已保存、未发送。
   - 给出草稿链接。
   - 在聊天窗口展示：
     - 邮件主题
     - 收件人
     - 抄送状态
     - 邮件正文内容

## HTML 模式

飞书用户 @：

```html
<a href="mailto:EMAIL" data-user-id="NUMERIC_USER_ID" style="cursor:pointer;transition:color 0.3s;color:rgb(20, 86, 240);padding:2px;text-decoration:none;border-radius:999em;margin:0px 2px" rel="nofollow noopener noreferrer">@姓名</a>
```

飞书文档链接：

```html
<span class="mention mention-link_URL mention-token_TOKEN mention-type_3 mention-uuid_UUID" id="link-to-mention-UUID"><a class="lark-doclink-href-3" href="URL" data-doclink="true" style="transition:color 0.3s;color:rgb(20, 86, 240);font-style:normal;margin-right:4px;cursor:pointer;text-decoration:none;white-space:pre-wrap" rel="nofollow noopener noreferrer">文档标题</a></span>
```

会议内容条目的加粗前缀：

```html
<li><span style="..."><b>核心定位：</b>正文内容。</span></li>
```
