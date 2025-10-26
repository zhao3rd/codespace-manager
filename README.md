# 🚀 GitHub Codespaces Manager (Multi-Account)

一个基于 Streamlit 的 GitHub Codespaces 管理工具，支持在一个界面中管理**多个 GitHub 账户**的 Codespace。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ 功能特性

- 🔐 **登录认证** - 需要用户名密码才能访问（Streamlit Secrets 存储）
- 👥 **多账户支持** - 在一个界面中管理多个 GitHub 账户的 Codespace
- 📋 **表格视图** - 全新表格布局，信息对齐清晰
- 🔄 **每行刷新** - 每个 Codespace 独立刷新按钮
- ▶️ **启动 Codespace** - 快速启动已停止的 Codespace
- ⏸️ **停止 Codespace** - 停止运行中的 Codespace 以节省资源
- 🔄 **保活功能** - 自动监控和维护 Codespace，防止意外停止
- ⏰ **自定义保活时长** - 0.5-24 小时可调，默认 4 小时
- ➕ **创建新 Codespace** - 为任何账户的仓库创建新的 Codespace
- 🔄 **实时状态更新** - 实时查看 Codespace 的状态变化
- ☁️ **云端 + 本地** - 同时支持本地运行和 Streamlit Cloud 部署
- 🔒 **安全存储** - 支持 Streamlit Secrets 和本地持久化存储
- 💾 **自动加载** - 重启后自动加载所有账户配置
- 🎨 **现代化 UI** - 简洁美观的表格界面

## 📋 系统要求

- Python 3.8 或更高版本
- GitHub Personal Access Token (需要 `codespace` 权限)

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd codespace-manager
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置登录（必需）

#### 本地开发

创建 `.streamlit/secrets.toml` 文件：

```toml
[login]
username = "admin"
password = "your_password"
```

或使用默认密码（username: `admin`, password: `admin`）

#### Streamlit Cloud

在 App Settings → Secrets 中添加：

```toml
[login]
username = "admin"
password = "your_password"
```

### 4. 配置账户

#### 方式一：本地开发 - 使用 JSON 文件

创建 `accounts.json` 文件：

```bash
cp accounts.json.example accounts.json
```

编辑 `accounts.json` 文件，添加你的账户：

```json
{
  "my_personal": "ghp_your_personal_token_here",
  "my_work": "ghp_your_work_token_here",
  "team_account": "ghp_your_team_token_here"
}
```

#### 方式二：Streamlit Cloud - 使用 Secrets

1. 部署到 Streamlit Cloud
2. 进入 App Settings → Secrets
3. 添加以下内容：

```toml
[login]
username = "admin"
password = "your_password"

# GitHub 存储配置（保活任务持久化，推荐配置）
[github_storage]
token = "ghp_your_token"
repo = "your-username/codespace-manager"
branch = "main"

[accounts]
my_personal = "ghp_your_personal_token_here"
my_work = "ghp_your_work_token_here"
team_account = "ghp_your_team_token_here"
```

> **重要**：配置 `github_storage` 可确保保活任务在 Streamlit Cloud 重启后不丢失。
> 详见：[云存储配置指南](CLOUD_STORAGE_SETUP.md)

#### 方式三：应用内添加（最简单）

1. 运行应用
2. 点击侧边栏的 "**➕ Add Account**" 按钮
3. 输入账户名称和 Token
4. 账户会自动保存到本地 JSON 文件

### 5. 运行应用

```bash
streamlit run streamlit_app.py
```

应用将在浏览器中自动打开（默认地址：`http://localhost:8501`）

### 6. 登录

使用配置的用户名和密码登录（默认：admin/admin）

## 🔑 获取 GitHub Token

每个账户都需要一个独立的 GitHub Personal Access Token。

### 步骤：

1. **访问 Token 设置页面**
   - 登录到对应的 GitHub 账户
   - 访问 [https://github.com/settings/tokens](https://github.com/settings/tokens)

2. **创建新 Token**
   - 点击 "Generate new token" → "Generate new token (classic)"
   - 设置 Token 名称（如：`Codespace Manager`）
   - 设置过期时间（建议选择合适的期限）

3. **选择权限**
   - ✅ 勾选 `codespace` 权限（完整访问）
   - 这是唯一需要的权限

4. **生成并保存**
   - 点击 "Generate token"
   - 复制生成的 Token（只会显示一次！）
   - 将 Token 添加到配置文件或应用中

5. **为其他账户重复**
   - 切换到其他 GitHub 账户
   - 重复上述步骤

## 📖 使用指南

### 账户管理

#### 查看所有账户

在 "**👥 Account Management**" 标签页中查看：
- 账户名称
- GitHub 用户名
- Token 来源（Streamlit Secrets 或本地存储）
- Token 预览（前 10 个字符）

#### 添加账户

1. 点击侧边栏的 "**➕ Add Account**"
2. 输入账户名称（自定义，用于区分）
3. 输入 GitHub Token
4. 点击 "**✅ Add**"

#### 删除账户

- 在侧边栏账户列表中点击 "**🗑️**" 按钮
- 注意：来自 Streamlit Secrets 的账户无法删除（显示 🔒）

### 查看 Codespaces

在 "**📋 All Codespaces**" 标签页中：
- 查看所有账户的 Codespace
- 按账户分组显示
- 每个 Codespace 显示：
  - 状态和名称
  - 所属仓库和分支
  - 机器类型和地理位置
  - 创建时间和最后使用时间
  - Web 访问链接

### 管理 Codespace

全新表格布局，每行显示一个 Codespace，操作按钮对齐在右侧：

| 列 | 说明 |
|---|---|
| Status | 状态图标（✅ 运行 / ⏸️ 停止） |
| Codespace / Repository | Codespace 名称、仓库、分支、链接 |
| Machine | 机器类型配置 |
| Location | 地理位置 |
| Last Used | 最后使用时间 |
| Actions | 操作按钮（刷新、启动/停止、保活管理） |

**操作按钮**：
- **🔄 刷新**：刷新单个 Codespace 状态
- **▶️ 启动**：启动已停止的 Codespace（带保活设置）
- **⏸️ 停止**：停止运行中的 Codespace
- **❌ 停止保活**：取消保活任务（保活激活时显示）

> **注意**：为了安全，删除 Codespace 功能已被移除。请在 GitHub 网页端删除 Codespace。

### 🔄 保活功能

**什么是保活？**

保活功能可以自动监控你的 Codespace，如果意外停止会自动重启，确保在指定时间内保持运行。

**如何使用**：
1. 点击 **▶️** 启动按钮
2. 在弹出的对话框中设置保活时长（0.5-24 小时，默认 4 小时）
3. 点击确认启动

**保活期间**：
- 显示 🔄 图标和剩余时间
- 页面每 10 分钟自动刷新检查状态
- 如果 Codespace 停止，自动重启
- 超过设定时间后自动取消保活
- **💾 自动保存，重启后恢复**

**停止保活**：
- 点击 **⏸️** 停止 Codespace（同时取消保活）
- 或点击 **❌** 只取消保活但不停止 Codespace

**持久化特性** 🆕：
- ✅ 保活任务自动保存
  - 本地：`keepalive_tasks.json` 文件
  - 云端：`codespace-manager/keepalive_tasks.json`（GitHub API）
- ✅ 应用重启后自动恢复未过期的任务
- ✅ **Streamlit Cloud 重启后数据不丢失**
- ✅ 使用你的私有 GitHub 仓库，安全可靠
- ✅ **多人同时使用不会冲突**（智能并发控制）

📖 详细说明：
- [保活功能指南](KEEPALIVE_GUIDE.md)
- [云存储配置](CLOUD_STORAGE_SETUP.md) ⭐ Streamlit Cloud 必读
- [并发控制 FAQ](CONCURRENCY_FAQ.md) - 多人使用说明

### 创建新 Codespace

在 "**➕ Create New**" 标签页：
1. **选择账户**：选择要使用的 GitHub 账户
2. **输入仓库**：格式 `owner/repo`（如 `octocat/Hello-World`）
3. **选择分支**：输入分支名称或 commit SHA
4. **选择机器类型**：根据项目需求选择
5. **选择地理位置**：选择离你最近的区域
6. **设置超时时间**：空闲多久后自动停止
7. 点击 "**🚀 Create Codespace**"

## 🏗️ 项目结构

```
codespace-manager/
├── app.py                          # Streamlit 主应用（多账户支持）
├── github_api.py                   # GitHub API 集成模块
├── config.py                       # 配置管理（多账户 + Secrets）
├── requirements.txt                # Python 依赖
├── accounts.json                   # 本地账户存储（gitignore）
├── accounts.json.example           # 账户配置示例
├── .streamlit/
│   ├── config.toml                # Streamlit 配置
│   └── secrets.toml.example       # Secrets 示例
├── .gitignore                     # Git 忽略文件
└── README.md                      # 项目文档
```

## ⚙️ 配置选项

在 `config.py` 中可以自定义以下默认值：

- `DEFAULT_MACHINE` - 默认机器类型
- `DEFAULT_LOCATION` - 默认地理位置
- `DEFAULT_IDLE_TIMEOUT` - 默认空闲超时时间
- `DEFAULT_REF` - 默认分支名称
- `ACCOUNTS_FILE` - 本地账户存储文件路径

## 🛠️ 技术栈

- **Streamlit** - Web 应用框架
- **Requests** - HTTP 请求库
- **Python-dotenv** - 环境变量管理
- **Pandas** - 数据处理

## 📝 API 权限说明

每个账户的 Token 需要以下 GitHub API 权限：

- `codespace` - 管理 Codespace 的完整权限
  - 列出 Codespace
  - 创建 Codespace
  - 启动/停止 Codespace
  - 删除 Codespace
  - 获取 Codespace 详情

## 🔒 安全注意事项

### 登录安全
- 🔐 应用需要登录才能访问
- 默认用户名/密码：`admin/admin`（**请修改！**）
- 登录凭证存储在 Streamlit Secrets 中

### Token 安全
- ⚠️ **永远不要将 Token 提交到版本控制系统**
- `accounts.json` 已在 `.gitignore` 中排除
- Streamlit Cloud Secrets 是安全加密的
- Token 在应用中以密码形式输入（不可见）
- 建议定期轮换 Token
- 只授予必要的最小权限（仅 `codespace`）
- 不同账户使用独立的 Token，避免权限交叉

### 💾 数据存储位置

**本地运行**：
- 账户数据：`accounts.json`（自动保存，重启后自动加载）
- 登录凭证：`.streamlit/secrets.toml`（默认 admin/admin）

**Streamlit Cloud**：
- 账户数据：Streamlit Secrets `[accounts]` 部分
- 登录凭证：Streamlit Secrets `[login]` 部分
- 所有数据重启后自动加载

📖 详细说明请查看：[SECURITY.md](SECURITY.md)

## ☁️ 部署到 Streamlit Cloud

### 步骤：

1. **推送代码到 GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **创建 Streamlit Cloud 应用**
   - 访问 [share.streamlit.io](https://share.streamlit.io/)
   - 连接你的 GitHub 仓库
   - 选择 `app.py` 作为主文件
   - 点击 Deploy

3. **配置 Secrets**
   - 进入 App Settings → Secrets
   - 添加账户配置（TOML 格式）：
   ```toml
   [accounts]
   account1 = "ghp_token1"
   account2 = "ghp_token2"
   ```

4. **完成**
   - 应用会自动部署
   - 可以从任何地方访问

### 混合使用 Secrets 和本地账户

- Streamlit Secrets 中的账户：🔒 锁定，无法在应用内删除
- 本地添加的账户：💾 可以在应用内删除
- 两者可以共存，Secrets 优先级更高

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙋 常见问题

### Q: 如何管理多个账户？
A: 有三种方式：
1. 在应用内点击 "Add Account" 逐个添加
2. 编辑 `accounts.json` 文件批量添加（本地）
3. 在 Streamlit Cloud Secrets 中配置（云端）

### Q: Streamlit Secrets 和本地文件有什么区别？
A: 
- **Streamlit Secrets**：云端加密存储，无法在应用内删除（🔒）
- **本地文件**：存储在 `accounts.json`，可以在应用内管理（💾）
- 两者可以同时使用，Secrets 优先级更高

### Q: 如何登录应用？
A: 
- 默认用户名密码：`admin/admin`
- 可以在 Streamlit Secrets 中配置自定义登录凭证
- 详见 `.streamlit/secrets.toml.example`

### Q: 账户数据存储在哪里？重启后还在吗？
A: 
- **本地运行**：存储在 `accounts.json` 文件，重启后自动加载
- **Streamlit Cloud**：存储在 Streamlit Secrets，重启后自动加载
- 所有数据都是持久化的，不会丢失

### Q: 为什么无法连接某个账户？
A: 请检查：
1. Token 是否正确
2. Token 是否有 `codespace` 权限
3. Token 是否已过期
4. 该 GitHub 账户是否存在
5. 网络连接是否正常

### Q: 如何删除账户？
A: 
- 本地添加的账户：点击侧边栏账户旁的 🗑️ 按钮
- Streamlit Secrets 的账户：需要在 Cloud 设置中修改 Secrets

### Q: 能否为不同的账户创建 Codespace？
A: 可以！在 "Create New" 标签页选择目标账户即可。

### Q: 应用支持多少个账户？
A: 理论上没有限制，但建议不超过 10 个账户以保持界面整洁。

### Q: Token 会被泄露吗？
A: 不会。Token 存储方式：
- 本地：`accounts.json` 文件（已在 .gitignore 中）
- 云端：Streamlit Secrets（加密存储）
- 界面：密码形式输入，不显示明文

### Q: 如何选择合适的机器类型？
A: 机器类型说明：
- `basicLinux32gb` - 2核 4GB RAM，适合小型项目
- `standardLinux32gb` - 4核 8GB RAM，适合中型项目
- `premiumLinux` - 8核 16GB RAM，适合大型项目
- `largePremiumLinux` - 16核 32GB RAM，适合超大型项目

### Q: 如何在本地和 Cloud 之间同步账户？
A: 
- 本地运行时使用 `accounts.json`
- Cloud 运行时使用 Streamlit Secrets
- 如果需要同步，手动将 `accounts.json` 内容复制到 Secrets 中

## 📞 联系方式

如有问题或建议，欢迎通过 Issue 联系。

## 🎯 使用场景

- 个人开发者管理个人和工作账户
- 团队管理多个组织账户的 Codespace
- 自由职业者管理不同客户的项目
- DevOps 团队集中管理开发环境

---

⭐ 如果这个项目对你有帮助，请给它一个星标！
