# ☁️ Streamlit Cloud 存储配置指南

## 问题说明

Streamlit Cloud Community 版本的文件系统是**临时的**，应用重启后会被清理。这意味着保活（keepalive）任务数据会丢失。

## 💡 解决方案：GitHub 存储

我们使用 **GitHub API** 将 keepalive 数据存储在你的私有仓库中。

### 优势

- ✅ **完全免费** - 无任何费用
- ✅ **简单易用** - 使用你已有的 GitHub 账户
- ✅ **安全可靠** - 数据存储在私有仓库
- ✅ **自动切换** - 本地用文件，云端用 GitHub
- ✅ **无需额外服务** - 不需要注册其他平台

---

## 🚀 配置步骤

### 步骤 1：获取 GitHub Token

1. 访问 [GitHub Settings - Tokens](https://github.com/settings/tokens)
2. 点击 **"Generate new token (classic)"**
3. 设置名称：`Codespace Manager Storage`
4. 勾选权限：
   - ✅ `repo` (完整仓库访问，用于存储数据)
   - ✅ `codespace` (管理 Codespace)
5. 点击 **"Generate token"**
6. **复制 token**（只显示一次！）

### 步骤 2：配置 Streamlit Secrets

#### 本地开发（可选）

创建 `.streamlit/secrets.toml`：

```toml
[login]
username = "admin"
password = "your_password"

[github_storage]
token = "ghp_your_github_token"
repo = "your-username/codespace-manager"
branch = "main"

[accounts]
account1 = "ghp_token1"
```

#### Streamlit Cloud（必需）

1. 打开你的 Streamlit Cloud 应用
2. 点击右上角 **Settings** → **Secrets**
3. 添加以下内容：

```toml
[login]
username = "admin"
password = "your_secure_password"

[github_storage]
token = "ghp_your_github_token"
repo = "your-username/codespace-manager"
branch = "main"

[accounts]
account1 = "ghp_token1"
account2 = "ghp_token2"
```

4. 点击 **Save**
5. 应用会自动重启

### 步骤 3：验证配置

1. 登录应用
2. 创建一个 keepalive 任务
3. 检查你的 GitHub 仓库，应该看到：
   - 📁 目录：`codespace-manager/`（自动创建）
   - 📄 文件：`codespace-manager/keepalive_tasks.json`
   - 📝 提交信息：`[Auto] Update keepalive tasks (1 active) - YYYY-MM-DD HH:MM:SS`
4. 重启应用
5. 保活任务应该自动恢复 ✅

> **注意**：GitHub API 会自动创建 `codespace-manager` 目录，无需手动创建。

---

## 📊 工作原理

### 自动后端选择

```
应用启动
    ↓
检查 Streamlit Secrets
    ↓
┌─────────────────────┐
│ 配置了 github_storage? │
└───┬─────────────┬───┘
   YES          NO
    ↓            ↓
 GitHub API   本地文件
    ↓            ↓
 云端存储     本地存储
```

### 数据存储位置

| 环境 | 存储方式 | 文件位置 |
|------|---------|---------|
| **本地开发** | 本地文件 | `keepalive_tasks.json` |
| **Streamlit Cloud（未配置）** | 本地文件（临时） | 重启后丢失 ❌ |
| **Streamlit Cloud（已配置）** | GitHub API | 你的仓库 ✅ |

### GitHub 存储流程

```
保活任务创建
    ↓
保存到 Session State
    ↓
调用 GitHub API
    ↓
自动创建 codespace-manager 目录（首次）
    ↓
创建/更新 keepalive_tasks.json
    ↓
提交到仓库（含任务数量）
    ↓
应用重启
    ↓
从 GitHub 加载数据
    ↓
恢复保活任务 ✅
```

### Commit 信息格式

每次更新的提交信息格式：
```
[Auto] Update keepalive tasks (N active) - 2025-10-26 20:30:00
```

其中：
- `[Auto]` - 自动提交标识
- `N active` - 当前活动任务数量
- 时间戳 - 更新时间

### 并发控制机制 🆕

**多人同时使用时的安全保障**：

```
用户 A 保存任务
    ↓
获取文件 SHA (版本标识)
    ↓
┌─ 用户 B 同时保存 ─┐
│   检测到冲突 (409) │
│         ↓          │
│   自动重试 (最多3次)│
│         ↓          │
│   读取最新远程数据  │
│         ↓          │
│   合并本地修改     │
│         ↓          │
└─ 重新提交成功 ✅  ─┘
```

**特性**：
- ✅ 自动冲突检测
- ✅ 智能数据合并
- ✅ 最多 3 次重试
- ✅ 本地修改优先
- ✅ 防止数据丢失

---

## 🔒 安全说明

### Token 权限

GitHub Token 需要 `repo` 权限：
- ✅ 读取仓库内容
- ✅ 创建/更新文件
- ✅ 提交更改

**注意**：Token 存储在 Streamlit Secrets 中，加密安全。

### 数据隐私

- ✅ 数据存储在**你的私有仓库**
- ✅ 只有你能访问
- ✅ 不会泄露给第三方
- ✅ 可以随时删除

### 最佳实践

1. 使用**私有仓库**
2. 定期**轮换 Token**
3. 只授予**必要权限**
4. 不要**公开分享** Secrets

---

## 🔍 故障排查

### ⚠️ 如果遇到问题

**详细的排查指南**：请查看 [故障排查指南](TROUBLESHOOTING.md) 📖

快速检查：

**检查清单**：
1. ✅ Streamlit Secrets 已正确配置
2. ✅ GitHub Token 有 `repo` 权限
3. ✅ 仓库名称格式正确（`owner/repo`）
4. ✅ 分支名称正确（通常是 `main`）
5. ✅ Token 未过期

**查看日志**：
1. Streamlit Cloud → Manage app → Logs
2. 查找 `🔧 Using GitHub storage backend` 信息
3. 查找错误信息（`❌ GitHub storage:`）

### Q: 配置后仍然丢失数据？

**调试步骤**：
1. 查看 Streamlit Cloud 日志（详细错误信息）
2. 检查 GitHub 仓库是否有 `codespace-manager/keepalive_tasks.json` 文件
3. 使用 `test_github_storage.py` 诊断工具
4. 参考 [故障排查指南](TROUBLESHOOTING.md)

### Q: GitHub API 限流？

**限制**：
- 未认证：60 次/小时
- 已认证：5000 次/小时

**当前使用**：
- 每 10 分钟检查一次
- 每小时 ~6 次 API 调用
- 冲突重试：最多额外 2 次/操作
- **完全在限制内** ✅

### Q: 多人同时使用会冲突吗？

**不会**！我们实现了并发控制：
1. 自动检测冲突（HTTP 409）
2. 最多重试 3 次
3. 自动合并远程和本地数据
4. 本地修改优先保存
5. 防止数据丢失

**示例场景**：
- 用户 A 创建保活任务 → 成功 ✅
- 用户 B 同时创建任务 → 检测到冲突
- 系统自动合并 → 两个任务都保存 ✅

### Q: GitHub 仓库没有看到文件？

**可能原因**：
1. 还没有创建 keepalive 任务
2. Token 权限不足
3. 仓库名称错误
4. 分支名称错误

**解决方法**：
1. 创建一个 keepalive 任务测试
2. 检查仓库中的 `codespace-manager/` 目录
3. 检查 Streamlit Cloud 日志
4. 验证 Token 有 `repo` 权限
5. 确认仓库和分支存在

**文件位置**：
```
your-repo/
└── codespace-manager/
    └── keepalive_tasks.json  ← 在这里
```

### Q: 第一次使用需要手动创建目录吗？

**不需要**！GitHub API 会自动创建 `codespace-manager` 目录。

**首次运行时**：
1. 创建第一个保活任务
2. 系统自动创建目录
3. 自动创建 JSON 文件
4. 自动提交到仓库 ✅

### Q: 可以用其他仓库吗？

**可以**！只需配置：
```toml
[github_storage]
repo = "your-username/another-repo"
```

建议使用当前仓库以简化管理。

### Q: Token 泄露怎么办？

**立即操作**：
1. 前往 [GitHub Tokens](https://github.com/settings/tokens)
2. 撤销泄露的 Token
3. 生成新 Token
4. 更新 Streamlit Secrets

---

## 🎯 其他免费方案（备选）

如果不想用 GitHub，还有这些选项：

### 1. JSONBin.io

```python
# 免费额度：100k 请求/月
url = "https://api.jsonbin.io/v3/b"
headers = {"X-Master-Key": "your-api-key"}
```

**优点**：专门的 JSON 存储
**缺点**：需要额外注册账号

### 2. Firebase Realtime Database

```python
# Google 提供，1GB 免费
import firebase_admin
```

**优点**：实时同步
**缺点**：配置较复杂

### 3. GitHub Gist

```python
# 使用 GitHub Gist 存储
gist_id = "your-gist-id"
```

**优点**：简单快速
**缺点**：默认公开（除非设为私密）

---

## 📊 方案对比

| 方案 | 免费额度 | 配置难度 | 安全性 | 推荐度 |
|------|---------|---------|--------|--------|
| **GitHub API** | 无限制 | ⭐ 低 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| JSONBin.io | 100k/月 | ⭐ 低 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Firebase | 1GB | ⭐⭐ 中 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| GitHub Gist | 无限制 | ⭐ 低 | ⭐⭐⭐ | ⭐⭐⭐ |

**推荐**：使用 GitHub API（默认已实现）

---

## ✅ 完成！

配置 GitHub 存储后：
- ✅ 保活任务持久化
- ✅ 应用重启后自动恢复
- ✅ 完全免费
- ✅ 安全可靠

查看你的 GitHub 仓库，享受云端持久化存储！🎉

