# 🚀 快速入门指南

## 5 分钟快速上手 GitHub Codespaces Manager

### 步骤 1: 安装依赖 (30 秒)

```bash
pip install -r requirements.txt
```

### 步骤 2: 运行应用 (10 秒)

```bash
streamlit run app.py
```

### 步骤 3: 添加第一个账户 (2 分钟)

1. 在侧边栏点击 **"➕ Add Account"**
2. 输入账户名称（如 `my_account`）
3. 输入你的 GitHub Token

#### 还没有 Token？

快速获取：
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. ✅ 勾选 `codespace` 权限
4. 复制生成的 token

### 步骤 4: 开始管理 (1 分钟)

- 查看所有 Codespace：切换到 **"📋 All Codespaces"** 标签
- 创建新 Codespace：切换到 **"➕ Create New"** 标签
- 管理账户：切换到 **"👥 Account Management"** 标签

## 🎯 多账户使用

### 添加更多账户

重复步骤 3，为每个 GitHub 账户添加独立的 token。

### 示例配置

#### 本地开发 - 直接编辑 JSON

创建 `accounts.json`：

```json
{
  "personal": "ghp_personal_token_xxx",
  "work": "ghp_work_token_xxx",
  "opensource": "ghp_opensource_token_xxx"
}
```

#### Streamlit Cloud - 使用 Secrets

在 Streamlit Cloud App Settings → Secrets 添加：

```toml
[accounts]
personal = "ghp_personal_token_xxx"
work = "ghp_work_token_xxx"
opensource = "ghp_opensource_token_xxx"
```

## ⚡ 常用操作

### 启动 Codespace
找到已停止的 Codespace → 点击 **▶️** 按钮

### 停止 Codespace
找到运行中的 Codespace → 点击 **⏸️** 按钮

### 删除 Codespace
找到要删除的 Codespace → 点击 **🗑️** 按钮

### 创建 Codespace
1. 切换到 "Create New" 标签
2. 选择账户
3. 输入仓库（如 `microsoft/vscode`）
4. 点击 "Create Codespace"

## 🔥 进阶技巧

### 批量查看

所有账户的 Codespace 会自动在一个页面显示，按账户分组。

### 快速刷新

点击侧边栏的 **🔄 Refresh All** 按钮更新所有状态。

### 删除账户

点击账户旁的 **🗑️** 按钮（仅限本地添加的账户）。

## ❓ 遇到问题？

### Token 无效
- 检查 token 是否包含 `codespace` 权限
- 检查 token 是否已过期

### 无法连接
- 检查网络连接
- 确认 GitHub 服务正常

### 看不到 Codespace
- 点击 "Refresh" 刷新
- 确认该账户确实有 Codespace

## 📚 更多信息

查看完整文档：[README.md](README.md)

---

🎉 享受管理 Codespace 的乐趣！

