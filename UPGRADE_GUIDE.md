# 🔄 升级指南 (v1.0.1 → v1.1.0)

## 📋 主要变更

### 1. ✅ 新增登录功能
应用现在需要登录才能访问。

### 2. ❌ 移除删除功能
为了安全，不再允许在应用中删除 Codespace。

### 3. 💾 数据持久化保证
明确说明账户数据的存储位置和重启后的加载机制。

---

## 🔐 登录配置（必需）

### 本地开发

创建 `.streamlit/secrets.toml` 文件：

```toml
[login]
username = "admin"
password = "your_password"

[accounts]
account1 = "ghp_token1"
account2 = "ghp_token2"
```

### Streamlit Cloud

在 App Settings → Secrets 添加：

```toml
[login]
username = "admin"
password = "your_password"

[accounts]
account1 = "ghp_token1"
account2 = "ghp_token2"
```

### 默认凭证

如果未配置，将使用：
- 用户名：`admin`
- 密码：`admin`

⚠️ **强烈建议修改默认密码！**

---

## 🗑️ 删除功能移除

### 为什么移除？
为了防止误操作删除重要的 Codespace。

### 如何删除 Codespace？
请访问 GitHub 网页端：
1. 打开 [GitHub Codespaces](https://github.com/codespaces)
2. 找到要删除的 Codespace
3. 点击 "..." → "Delete"

### 应用中还能做什么？
- ✅ 查看 Codespace
- ✅ 启动 Codespace
- ✅ 停止 Codespace
- ✅ 创建 Codespace
- ❌ ~~删除 Codespace~~（已移除）

---

## 💾 数据存储说明

### 存储位置

| 运行环境 | 账户数据 | 登录凭证 |
|---------|---------|---------|
| **本地** | `accounts.json` | `.streamlit/secrets.toml` |
| **云端** | Streamlit Secrets `[accounts]` | Streamlit Secrets `[login]` |

### 数据持久化

✅ **重启后会保留**：
- 所有账户配置
- 所有 GitHub Tokens
- 登录凭证

❌ **重启后会丢失**：
- 登录状态（需要重新登录）
- Session 缓存

### 如何确认数据已保存？

**本地**：
```bash
# 检查文件是否存在
ls accounts.json
ls .streamlit/secrets.toml
```

**云端**：
在 Streamlit Cloud 的 App Settings → Secrets 中查看配置。

---

## 🚀 升级步骤

### 方式一：拉取最新代码

```bash
git pull origin main
pip install -r requirements.txt
```

### 方式二：手动更新文件

只需更新以下文件：
- `streamlit_app.py`（原 `app.py`）
- `requirements.txt`
- `.streamlit/secrets.toml.example`

### 配置登录

1. 创建 `.streamlit/secrets.toml`（本地）或配置 Secrets（云端）
2. 添加登录凭证
3. 启动应用

---

## 📖 新增文档

- `SECURITY.md` - 安全和存储详细说明
- `UPGRADE_GUIDE.md` - 本升级指南

---

## ❓ 常见问题

### Q: 升级后无法访问应用？
A: 需要先配置登录凭证，或使用默认 `admin/admin`。

### Q: 我的账户数据还在吗？
A: 是的！`accounts.json` 或 Streamlit Secrets 中的数据不会丢失。

### Q: 如何迁移到新版本？
A: 
1. 备份 `accounts.json`
2. 更新代码
3. 配置登录凭证
4. `accounts.json` 会自动加载

### Q: 为什么不能删除 Codespace 了？
A: 为了安全。请在 GitHub 网页端删除。

### Q: 默认密码安全吗？
A: 不安全！请立即修改为强密码。

---

## 🔄 回滚到旧版本

如果需要回滚：

```bash
git checkout v1.0.1
pip install -r requirements.txt
```

注意：旧版本没有登录功能，也没有删除功能的限制。

---

## 📞 需要帮助？

- 查看 [SECURITY.md](SECURITY.md) 了解安全配置
- 查看 [README.md](README.md) 了解完整功能
- 提交 Issue 获取支持

---

**升级愉快！** 🎉

