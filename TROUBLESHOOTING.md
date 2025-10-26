# 🔧 故障排查指南

## ❌ 问题：Streamlit Cloud 中保活任务没有保存到 GitHub

如果你在 Streamlit Cloud 中运行时，保活任务没有成功保存到 GitHub 仓库，请按以下步骤排查。

---

## 📋 排查清单

### ✅ 第 1 步：检查 Secrets 配置

#### 1.1 确认 Secrets 存在

登录 **Streamlit Cloud** → 你的应用 → **Settings** → **Secrets**

确认有以下内容：

```toml
[github_storage]
token = "ghp_your_actual_token_here"
repo = "your-username/your-repository"
branch = "main"
```

**常见错误**：
- ❌ 拼写错误：`[github_storge]` (少了 a)
- ❌ 缺少引号：`token = ghp_xxx` (应该是 `"ghp_xxx"`)
- ❌ 多余空格：`repo = " username/repo "` (引号内有空格)
- ❌ 格式错误：使用了 JSON 格式而不是 TOML

**正确格式**：
```toml
[github_storage]
token = "ghp_1234567890abcdefghijklmnopqrstuvwxyz1234"
repo = "zhangsan/codespace-manager"
branch = "main"
```

#### 1.2 验证配置值

| 配置项 | 格式 | 示例 | 说明 |
|--------|------|------|------|
| `token` | `ghp_` 开头 | `ghp_abc123...` | GitHub Personal Access Token |
| `repo` | `owner/name` | `zhangsan/my-repo` | 仓库完整路径（不是 URL） |
| `branch` | 分支名 | `main` 或 `master` | 目标分支名称 |

---

### ✅ 第 2 步：检查 GitHub Token 权限

#### 2.1 Token 范围

访问 https://github.com/settings/tokens

找到你使用的 Token，确认勾选了以下权限：

**必需权限**：
- ✅ `repo` - Full control of private repositories
  - ✅ `repo:status` - Access commit status
  - ✅ `repo_deployment` - Access deployment status
  - ✅ `public_repo` - Access public repositories
  - ✅ `repo:invite` - Access repository invitations
  - ✅ `security_events` - Read and write security events

**简单判断**：勾选顶层的 `repo` 即可（会自动包含所有子权限）

#### 2.2 Token 有效性

- ❌ Token 过期？检查 Token 的有效期
- ❌ Token 被删除？生成新 Token
- ❌ Token 权限不足？重新生成并勾选 `repo` 权限

---

### ✅ 第 3 步：检查仓库配置

#### 3.1 仓库路径格式

**正确格式**：
```
owner/repository
```

**示例**：
- ✅ `zhangsan/codespace-manager`
- ✅ `my-org/my-project`
- ❌ `github.com/zhangsan/codespace-manager` （不要包含域名）
- ❌ `zhangsan/codespace-manager.git` （不要包含 .git）
- ❌ `https://github.com/zhangsan/codespace-manager` （不要用 URL）

#### 3.2 仓库权限

确认：
1. 仓库存在（没有被删除）
2. Token 对应的用户有写权限
3. 如果是私有仓库，Token 有访问权限

#### 3.3 分支名称

常见分支名：
- `main` （GitHub 新仓库默认）
- `master` （旧仓库默认）

**检查方法**：
1. 访问 GitHub 仓库
2. 查看左上角分支选择器
3. 确认分支名称与配置一致

---

### ✅ 第 4 步：使用诊断工具

#### 4.1 运行诊断脚本

我已经创建了一个诊断工具：`test_github_storage.py`

**在 Streamlit Cloud 上运行**：

1. 将 `test_github_storage.py` 添加到你的仓库
2. 在 Streamlit Cloud 创建新应用，指向这个文件
3. 或者临时修改 `streamlit_app.py`：

```python
# 在文件开头添加
import sys
if len(sys.argv) > 1 and sys.argv[1] == '--test':
    from test_github_storage import test_github_storage
    test_github_storage()
    sys.exit(0)
```

#### 4.2 查看应用日志

**Streamlit Cloud 查看日志**：

1. 打开你的 Streamlit Cloud 应用
2. 点击右下角的 **Manage app** 
3. 选择 **Logs** 标签
4. 查找以下信息：

**成功标识**：
```
🔧 Using GitHub storage backend
   Repo: your-username/your-repo
   Branch: main
   Token: ✅ configured
✅ GitHub storage: Successfully saved 1 tasks
```

**失败标识**：
```
❌ GitHub storage: GitHub API error 404: Not Found
或
❌ GitHub storage: GitHub API error 401: Bad credentials
或
❌ GitHub storage: GitHub API error 403: Resource not accessible by integration
```

---

### ✅ 第 5 步：常见错误与解决方案

#### 错误 1：404 Not Found

```
❌ GitHub API error 404: Not Found
```

**原因**：
- 仓库路径错误
- 仓库不存在
- Token 没有访问权限（私有仓库）

**解决方案**：
1. 检查仓库路径格式：`owner/repository`
2. 访问 GitHub 确认仓库存在
3. 确认 Token 有仓库访问权限

#### 错误 2：401 Bad credentials

```
❌ GitHub API error 401: Bad credentials
```

**原因**：
- Token 无效或已过期
- Token 格式错误

**解决方案**：
1. 重新生成 GitHub Token
2. 确认 Token 格式：以 `ghp_` 开头
3. 更新 Streamlit Secrets

#### 错误 3：403 Forbidden

```
❌ GitHub API error 403: Resource not accessible by integration
```

**原因**：
- Token 权限不足
- 仓库禁止了 API 访问

**解决方案**：
1. 检查 Token 是否有 `repo` 权限
2. 重新生成 Token 并勾选 `repo`
3. 更新 Streamlit Secrets

#### 错误 4：422 Unprocessable Entity

```
❌ GitHub API error 422: Invalid request
```

**原因**：
- 分支名称错误
- 数据格式问题

**解决方案**：
1. 检查分支名称（`main` vs `master`）
2. 确认分支存在

#### 错误 5：Secrets 未配置

```
ℹ️ 'github_storage' not found in Streamlit secrets
📁 Falling back to local file storage
```

**原因**：
- Secrets 没有配置
- Secrets 配置名称错误

**解决方案**：
1. 在 Streamlit Cloud → Settings → Secrets 添加配置
2. 确认配置名称为 `[github_storage]`（不是其他名称）
3. 保存并重启应用

---

### ✅ 第 6 步：手动测试 GitHub API

如果以上步骤都正常，可以手动测试 GitHub API：

#### 6.1 使用 curl 测试（命令行）

```bash
# 替换以下变量
TOKEN="ghp_your_token_here"
REPO="username/repository"

# 测试 1: 检查 Token
curl -H "Authorization: token $TOKEN" \
     https://api.github.com/user

# 测试 2: 检查仓库
curl -H "Authorization: token $TOKEN" \
     https://api.github.com/repos/$REPO

# 测试 3: 列出文件
curl -H "Authorization: token $TOKEN" \
     https://api.github.com/repos/$REPO/contents
```

#### 6.2 使用在线工具测试

访问：https://hoppscotch.io/

1. Method: `GET`
2. URL: `https://api.github.com/repos/your-username/your-repo`
3. Headers:
   - `Authorization`: `token ghp_your_token_here`
   - `Accept`: `application/vnd.github+json`
4. Send

**期望结果**：返回 200，显示仓库信息

---

## 🎯 完整诊断流程

### 快速检查脚本

在 Streamlit Cloud 应用中，查看日志输出：

```
启动应用时会显示：

💾 Saving 1 keepalive task(s)...
🔧 Using GitHub storage backend
   Repo: username/repository
   Branch: main
   Token: ✅ configured
✅ GitHub storage: Successfully saved 1 tasks
✅ Successfully saved to GitHub
```

如果看到这些信息，说明配置正确！

### 如果仍然失败

1. **复制完整的错误日志**
2. **检查是否是 Token 还是 Repo 的配置问题**
3. **尝试使用不同的仓库测试**
4. **确认 GitHub 服务状态**：https://www.githubstatus.com/

---

## 📝 配置模板

### 完整的 Streamlit Secrets 配置

```toml
# Login credentials
[login]
username = "admin"
password = "your_password"

# GitHub Storage (必需，用于保活任务持久化)
[github_storage]
token = "ghp_your_github_token_here"
repo = "your-username/codespace-manager"
branch = "main"

# Multiple GitHub accounts
[accounts]
personal = "ghp_personal_token"
work = "ghp_work_token"
```

### 最小配置（仅 GitHub 存储）

```toml
[github_storage]
token = "ghp_1234567890abcdefghijklmnopqrstuvwxyz1234"
repo = "zhangsan/my-repo"
branch = "main"
```

---

## ✅ 验证成功

配置成功后，你应该能在 GitHub 仓库中看到：

```
your-repository/
└── codespace-manager/
    └── keepalive_tasks.json
```

提交信息类似：
```
[Auto] Update keepalive tasks (1 active) - 2025-10-26 20:30:00
```

---

## 🆘 仍然无法解决？

如果以上所有步骤都尝试过仍然不行，请提供以下信息：

1. **Streamlit Cloud 日志**（完整的错误信息）
2. **Secrets 配置**（隐藏 Token，只显示格式）
3. **Token 权限截图**（从 GitHub Settings → Tokens）
4. **仓库设置**（公开/私有，权限）

创建 Issue 时包含这些信息能更快得到帮助！

---

## 📚 相关文档

- [云存储配置指南](CLOUD_STORAGE_SETUP.md)
- [并发控制 FAQ](CONCURRENCY_FAQ.md)
- [安全指南](SECURITY.md)

