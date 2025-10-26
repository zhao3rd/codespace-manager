# 🔐 安全与存储说明

## 🔑 登录功能

### 配置登录凭证

应用需要登录才能访问，用户名和密码存储在 Streamlit Secrets 中。

#### Streamlit Cloud 配置

1. 进入 App Settings → Secrets
2. 添加登录配置：

```toml
[login]
username = "admin"
password = "your_secure_password"
```

#### 本地开发配置

创建 `.streamlit/secrets.toml` 文件：

```toml
[login]
username = "admin"
password = "your_secure_password"
```

⚠️ **注意**：`.streamlit/secrets.toml` 已在 `.gitignore` 中，不会被提交到版本控制。

### 默认凭证

如果未配置 Streamlit Secrets，将使用默认凭证：
- **用户名**: `admin`
- **密码**: `admin`

⚠️ **强烈建议**：在生产环境中修改默认密码！

### 登出

点击侧边栏底部的 "🔓 Logout" 按钮即可退出登录。

---

## 💾 账户和 Token 存储

### 存储位置

应用支持两种存储方式，会自动从两个位置加载账户：

#### 1. 本地存储（本地运行）

**文件位置**：`accounts.json`

**格式**：
```json
{
  "account1": "ghp_token1",
  "account2": "ghp_token2"
}
```

**特点**：
- ✅ 本地文件，重启后自动加载
- ✅ 可以手动编辑
- ✅ 在应用内添加的账户会保存到此文件
- ⚠️ 已在 `.gitignore` 中，不会被提交到 Git

#### 2. Streamlit Secrets（云端运行）

**配置位置**：Streamlit Cloud → App Settings → Secrets

**格式**：
```toml
[accounts]
account1 = "ghp_token1"
account2 = "ghp_token2"
```

**特点**：
- ✅ 云端加密存储
- ✅ 重启后自动加载
- ✅ 更安全
- 🔒 无法在应用内删除（锁定）

### 存储优先级

当同时存在本地文件和 Streamlit Secrets 时：

```
Streamlit Secrets 优先级更高
    ↓
本地 accounts.json
    ↓
应用内手动添加
```

### 自动重新加载

✅ **重启后自动加载**

- 本地运行：从 `accounts.json` 加载
- 云端运行：从 Streamlit Secrets 加载
- 两者可以混合使用

### 添加账户的三种方式

#### 方式一：应用内添加
1. 登录应用
2. 点击侧边栏 "➕ Add Account"
3. 输入账户名和 token
4. 自动保存到 `accounts.json`

#### 方式二：编辑 accounts.json
```json
{
  "personal": "ghp_personal_token",
  "work": "ghp_work_token"
}
```

#### 方式三：配置 Streamlit Secrets
```toml
[accounts]
personal = "ghp_personal_token"
work = "ghp_work_token"
```

---

## 🔒 安全最佳实践

### 1. 保护敏感文件

以下文件已在 `.gitignore` 中：
- ✅ `accounts.json` - 本地账户存储
- ✅ `keepalive_tasks.json` - 保活任务数据 🆕
- ✅ `.streamlit/secrets.toml` - 本地 secrets
- ✅ `.env` - 环境变量

**永远不要将这些文件提交到版本控制！**

### 2. 使用强密码

登录密码建议：
- 至少 12 个字符
- 包含大小写字母、数字、特殊字符
- 定期更换

### 3. Token 安全

GitHub Token：
- 只授予必要的权限（`codespace`）
- 定期轮换 token
- 不在代码中硬编码
- 发现泄露立即撤销

### 4. 云端部署

在 Streamlit Cloud 上：
- ✅ 所有 Secrets 都是加密存储
- ✅ 只有应用可以访问
- ✅ 不会在日志中显示
- ✅ 支持环境隔离

### 5. 访问控制

- 应用需要登录才能访问
- 可以为不同用途创建不同账户
- 定期审查访问日志

---

## 🔄 数据持久化

### 应用重启后

✅ **会保留**：
- 登录凭证（Secrets）
- GitHub 账户配置（accounts.json / Secrets）
- GitHub Tokens（accounts.json / Secrets）
- **保活任务（keepalive_tasks.json）** 🆕
  - 自动恢复未过期的保活任务
  - 继续监控和维护

❌ **不会保留**：
- 登录状态（需要重新登录）
- Session 缓存（Manager 实例、用户信息等）
- 临时的 Codespace 状态

### 数据恢复

如果数据丢失：
1. 检查 `accounts.json` 文件是否存在
2. 检查 Streamlit Secrets 是否配置正确
3. 重新添加账户

---

## ❓ 常见问题

### Q: 重启后需要重新添加账户吗？
A: **不需要**。账户会自动从 `accounts.json` 或 Streamlit Secrets 加载。

### Q: 账户数据会丢失吗？
A: 不会。本地使用 `accounts.json` 文件持久化，云端使用 Streamlit Secrets。

### Q: 如何备份账户数据？
A: 
- 本地：复制 `accounts.json` 文件
- 云端：导出 Streamlit Secrets 配置

### Q: 可以不登录直接使用吗？
A: 不可以。登录是必需的，这是为了保护敏感的 Codespace 操作。

### Q: 忘记密码怎么办？
A: 
- 本地：删除或修改 `.streamlit/secrets.toml`，会使用默认密码 `admin/admin`
- 云端：在 Streamlit Cloud 设置中修改 Secrets

### Q: Token 会被泄露吗？
A: 
- Token 存储在本地文件或加密的 Secrets 中
- 不会在界面完整显示（只显示前 10 个字符）
- 不会被提交到 Git（已在 .gitignore）

---

## 📞 安全问题报告

如果发现安全问题，请通过 Issue 报告，我们会尽快处理。

**请勿在公开 Issue 中暴露敏感信息！**

