# 飞书 CLI 部署与文档操作规范

## 目标
- 为其他用户或 AI 助手提供一份可直接复用的飞书 CLI 部署与文档操作规范。
- 固化本项目中已验证通过的安装、授权、创建云文档流程。
- 明确创建文件夹、创建云文档所需的权限与常见失败原因。

## 适用场景
- 用户希望让 AI 助手在本机安装并配置 `@larksuite/cli`。
- 用户希望让 AI 助手在飞书云盘目录中创建文档、文件夹或后续资料。
- 用户希望将本地产物、需求文档、规则说明同步到飞书。

## 先决条件
- 本机已安装 `Node.js` 与 `npm`。
- 可访问飞书开放平台与 GitHub Release。
- 已完成飞书开放平台应用配置。
- 若需要在用户个人目录下操作文件，优先使用 `user` 身份而非 `bot` 身份。

## 标准目标
- 安装 `@larksuite/cli`
- 安装 `larksuite/cli` 对应 skills
- 初始化 CLI 配置
- 完成用户授权
- 在指定飞书目录下创建云文档
- 在具备额外权限时创建文件夹

## 标准命令
```powershell
npm install -g @larksuite/cli
npx skills add https://github.com/larksuite/cli -y -g
lark-cli config init --new
lark-cli auth login --domain drive --domain docs
```

## Windows 已验证部署流程
### 1. 检查运行环境
```powershell
node --version
npm --version
```

### 2. 安装 `@larksuite/cli`
标准命令：
```powershell
npm install -g @larksuite/cli
```

### 3. 若 `npm install -g @larksuite/cli` 失败
常见现象：
- npm 报 `postinstall` 失败
- 包目录已存在，但 `bin/lark-cli.exe` 未落地
- Windows 下出现 `EBUSY`、残留文件占用、或下载过程无输出

已验证可行的修复思路：
1. 先卸载残留包并清理缓存。
2. 重新安装 npm 包壳。
3. 若二进制仍未自动落地，则手动从 GitHub Release 下载 Windows 发布包。
4. 解压后将 `lark-cli.exe` 放到：
   - `C:\Users\<用户名>\AppData\Roaming\npm\node_modules\@larksuite\cli\bin\`
5. 再执行：
```powershell
lark-cli --version
```

验证通过标准：
- 能输出类似 `lark-cli version 1.0.2`

## Skills 安装规范
### 标准命令
```powershell
npx skills add https://github.com/larksuite/cli -y -g
```

### Windows 路径问题
本项目实测遇到过以下问题：
- `skills` 在 Windows + Git for Windows 下克隆仓库时，临时目录被错误拼接成 `/cygdrive/.../C:\...`
- 表现为 `Failed to clone repository`

已验证可行的规避方式：
1. 先把仓库克隆到本地相对路径，例如：
```powershell
git clone https://github.com/larksuite/cli.git larksuite-cli-skills
```
2. 再将 `TEMP` 和 `TMP` 指向当前目录下的相对路径：
```powershell
mkdir tmp
cmd /c "set TEMP=tmp&& set TMP=tmp&& npx skills add .\larksuite-cli-skills -y -g"
```

验证通过标准：
- 输出 `Installed 19 skills`

## CLI 配置初始化
```powershell
lark-cli config init --new
```

执行后会进入飞书网页配置流程，成功后可用以下命令验证：
```powershell
lark-cli config show
```

验证通过标准：
- 能看到 `appId`
- 能看到 `brand`
- 配置文件路径可读

## 用户授权流程
### 推荐方式
对于用户个人目录、个人飞书文档、个人云盘文件夹操作，必须优先使用 `user` 身份。

标准流程：
```powershell
lark-cli auth login --domain drive --domain docs --no-wait --json
```

然后让 AI 助手读取返回的 `verification_url`，让用户打开浏览器完成授权。

后台等待授权：
```powershell
lark-cli auth login --device-code "<device_code>"
```

授权完成后验证：
```powershell
lark-cli auth status
lark-cli auth list
```

验证通过标准：
- `identity` 为 `user`
- `tokenStatus` 为 `valid`

## 审批与重授权规则
- 若用户刚在飞书开放平台界面提交权限申请并显示审核通过，之前已经发起的旧授权流程可能仍然失败。
- 遇到 `authorization failed: The app is pending approval.` 时，不要继续复用旧的 `device_code`。
- 应重新发起一次新的 `lark-cli auth login --domain ... --no-wait --json`。

## 云文档创建流程
### 高层命令
```powershell
lark-cli docs +create --title "<标题>" --folder-token "<目录token>" --markdown "<Markdown正文>" --as user
```

### 适用条件
- 当前用户身份已登录
- 应用已具备文档创建相关 scope
- 当前用户对目标目录具有编辑权限

### 已验证结果
- 在目标目录中创建云文档是可行的
- 本项目已成功创建一篇测试文档

### 常见用途
- 创建说明文档
- 写入规则、流程、需求说明
- 生成给协作者阅读的交付文档

## 文件夹创建流程
### 接口
官方接口为：
- `POST /open-apis/drive/v1/files/create_folder`

参考文档：
- [飞书创建文件夹接口](https://open.feishu.cn/document/server-docs/docs/drive-v1/folder/create_folder)

### 所需权限
以下二选一即可：
- `drive:drive`
- `space:folder:create`

### 请求体
```json
{
  "name": "ai agent",
  "folder_token": "<父目录token>"
}
```

### 风险说明
- 即便已经拿到 `user` 身份，如果未开通上述 scope，也无法创建文件夹。
- 本项目实际验证中，云文档创建成功，但文件夹创建仍因缺少 `drive:drive` / `space:folder:create` 而被阻塞。

## 文档操作与目录操作的权限区别
- 创建云文档：更依赖 `docs/docx` 相关权限，以及目标目录的编辑权限。
- 创建文件夹：额外依赖 `drive:drive` 或 `space:folder:create`。
- 不能因为“已经能创建文档”，就推断“已经能创建文件夹”。

## AI 助手执行规范
### 执行顺序
1. 检查 `node`、`npm`
2. 安装 `@larksuite/cli`
3. 安装 `larksuite/cli` skills
4. 初始化配置
5. 登录用户身份
6. 检查 scope 与目录权限
7. 先创建云文档验证链路
8. 再创建文件夹

### 行为原则
- 先用高层命令，后用通用 API。
- 先验证身份和 scope，再操作目标目录。
- 若授权状态发生变化，重新发起登录，不复用旧授权流程。
- 若 Windows 下安装失败，优先按本规范中的已验证 workaround 处理。
- 对创建失败的场景，必须区分是：
  - 安装失败
  - 未登录用户
  - app 未审批
  - 缺 scope
  - 目标目录无编辑权限

## 给其他用户的推荐话术
```text
请帮我安装并配置飞书 CLI，并完成以下动作：
1. 检查 node 和 npm 是否可用
2. 安装 @larksuite/cli
3. 安装 larksuite/cli 对应 skills
4. 初始化配置
5. 发起 drive + docs 的用户授权，并在需要时让我打开链接完成授权
6. 检查当前用户态是否有效
7. 在我提供的飞书目录下先创建一篇测试云文档
8. 如果需要创建文件夹，请先检查是否具备 drive:drive 或 space:folder:create

如果 Windows 安装失败，请按项目中已验证的 workaround 自动处理，不要只告诉我命令。
```

## 故障排查清单
- `lark-cli --version` 是否可正常输出
- `lark-cli config show` 是否可读
- `lark-cli auth status` 是否为 `user`
- `lark-cli auth check --scope "<scope列表>"` 是否通过
- 目标目录是否由当前用户可编辑
- 失败时到底是文档创建失败，还是仅文件夹创建失败

## 当前版本
- v1.0：基于本项目实际部署、授权、创建飞书文档的完整验证过程整理
