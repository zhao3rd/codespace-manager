# 🚀 快速排查：GitHub 存储问题

## ⚡ 3 分钟快速诊断

### 第 1 步：检查 Secrets 配置 (30秒)

在 Streamlit Cloud → Settings → Secrets 中确认：

```toml
[github_storage]
token = "ghp_xxxxx"              ← 必须以 ghp_ 开头
repo = "username/repository"     ← 格式：owner/repo（不是 URL）
branch = "main"                  ← 通常是 main 或 master
```

**常见错误**：
- ❌ `[github_storge]` → ✅ `[github_storage]`
- ❌ `"github.com/user/repo"` → ✅ `"user/repo"`
- ❌ 缺少引号 → ✅ 用引号包裹所有值

---

### 第 2 步：检查 Token 权限 (1分钟)

访问：https://github.com/settings/tokens

你的 Token 必须勾选：
- ✅ **`repo`** - Full control of private repositories

**如何判断**：
- Token 以 `ghp_` 开头 ✅
- Token 没有过期 ✅
- Token 有 `repo` 权限 ✅

---

### 第 3 步：查看日志 (1分钟)

在 Streamlit Cloud 应用中：

**Manage app** → **Logs** → 搜索以下关键词：

#### ✅ 成功的日志：
```
🔧 Using GitHub storage backend
   Repo: username/repository
   Branch: main
   Token: ✅ configured
✅ GitHub storage: Successfully saved 1 tasks
```

#### ❌ 失败的日志：

**情况 1：Token 无效**
```
❌ GitHub API error 401: Bad credentials
```
→ 重新生成 Token

**情况 2：仓库不存在**
```
❌ GitHub API error 404: Not Found
```
→ 检查仓库路径格式

**情况 3：权限不足**
```
❌ GitHub API error 403: Resource not accessible
```
→ Token 需要 `repo` 权限

**情况 4：未配置**
```
ℹ️ 'github_storage' not found in Streamlit secrets
📁 Falling back to local file storage
```
→ 添加 Secrets 配置

---

## 🎯 5 个最常见问题

### 1. 仓库路径格式错误

❌ 错误：
```toml
repo = "github.com/username/repository"
repo = "username/repository.git"
repo = "https://github.com/username/repository"
```

✅ 正确：
```toml
repo = "username/repository"
```

### 2. Token 权限不足

**症状**：403 Forbidden

**解决**：
1. 访问 https://github.com/settings/tokens
2. 编辑或重新生成 Token
3. 勾选 `repo` 权限
4. 更新 Streamlit Secrets

### 3. 分支名称错误

**常见问题**：配置的是 `main`，实际是 `master`

**检查方法**：
1. 访问你的 GitHub 仓库
2. 查看左上角分支选择器
3. 确认默认分支名称
4. 更新 Secrets 配置

### 4. Secrets 格式错误

❌ 缺少引号：
```toml
token = ghp_xxxxx
```

❌ 使用 JSON 格式：
```json
{
  "token": "ghp_xxxxx"
}
```

✅ 正确的 TOML 格式：
```toml
token = "ghp_xxxxx"
```

### 5. Token 过期

**症状**：之前能用，现在突然 401 错误

**解决**：
1. 检查 Token 有效期
2. 生成新 Token
3. 更新 Streamlit Secrets

---

## 🔧 使用诊断工具

### 方法 1：运行诊断脚本

1. 将 `test_github_storage.py` 添加到仓库
2. 在 Streamlit Cloud 创建新应用指向该文件
3. 运行所有诊断测试

### 方法 2：手动测试 GitHub API

使用 curl 测试（替换 TOKEN 和 REPO）：

```bash
# 测试 Token
curl -H "Authorization: token ghp_your_token" \
     https://api.github.com/user

# 测试仓库访问
curl -H "Authorization: token ghp_your_token" \
     https://api.github.com/repos/username/repository
```

期望返回：200 OK

---

## ✅ 验证成功

配置成功后，你应该看到：

### 在日志中：
```
✅ GitHub storage: Successfully saved 1 tasks
```

### 在 GitHub 仓库中：
```
your-repository/
└── codespace-manager/
    └── keepalive_tasks.json
```

### 提交信息：
```
[Auto] Update keepalive tasks (1 active) - 2025-10-26 20:30:00
```

---

## 📚 详细文档

还有问题？查看：

- 📖 [完整故障排查指南](TROUBLESHOOTING.md) - 详细的问题分析
- 🔧 [云存储配置](CLOUD_STORAGE_SETUP.md) - 完整配置说明
- 🔐 [安全指南](SECURITY.md) - Token 和权限说明

---

## 💡 快速配置模板

复制粘贴到 Streamlit Cloud Secrets：

```toml
[github_storage]
token = "ghp_把你的token粘贴到这里"
repo = "你的用户名/你的仓库名"
branch = "main"
```

**记得替换**：
- `ghp_把你的token粘贴到这里` → 你的实际 Token
- `你的用户名/你的仓库名` → 如 `zhangsan/codespace-manager`

保存后重启应用即可！✅

