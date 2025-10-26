# 📦 Streamlit Cloud 部署指南

## ✅ 文件名规范

本项目已按照 Streamlit Cloud 规范配置：

- ✅ 入口文件：`streamlit_app.py`（Streamlit Cloud 默认识别）
- ✅ 配置目录：`.streamlit/`
- ✅ 依赖文件：`requirements.txt`

## 🚀 部署步骤

### 1. 推送代码到 GitHub

```bash
git add .
git commit -m "Ready for Streamlit Cloud deployment"
git push origin main
```

### 2. 在 Streamlit Cloud 创建应用

1. 访问 [share.streamlit.io](https://share.streamlit.io/)
2. 点击 **"New app"**
3. 选择你的 GitHub 仓库
4. **主文件路径**：
   - 留空（自动识别 `streamlit_app.py`）
   - 或手动填写：`streamlit_app.py`
5. 点击 **"Deploy"**

### 3. 配置 Secrets

部署完成后，配置 Secrets：

1. 点击右上角 **Settings** → **Secrets**
2. 添加以下内容：

```toml
# 登录凭证（必需）
[login]
username = "admin"
password = "your_secure_password"

# GitHub 账户配置
[accounts]
account1 = "ghp_your_token_1"
account2 = "ghp_your_token_2"
```

3. 点击 **Save**
4. 应用会自动重启

## 🎯 关键配置

### 文件名要求

Streamlit Cloud 默认查找以下文件名（优先级从高到低）：

1. `streamlit_app.py` ✅ **我们使用这个**
2. `app.py`
3. `main.py`
4. 自定义（需手动指定）

### 目录结构

```
your-repo/
├── streamlit_app.py          # ✅ 主应用（自动识别）
├── requirements.txt          # ✅ 依赖文件
├── .streamlit/
│   └── config.toml          # 主题配置（可选）
├── config.py                # 应用配置
├── github_api.py            # API 模块
└── accounts.json.example    # 示例文件
```

## ⚙️ Streamlit Cloud 设置

### 基本设置

- **Repository**: 你的 GitHub 仓库
- **Branch**: `main` 或其他分支
- **Main file path**: 留空或 `streamlit_app.py`

### 高级设置

- **Python version**: 3.8+ (自动检测)
- **Custom subdomain**: 可选自定义域名
- **Secrets**: 通过 UI 配置

## 🔐 Secrets 配置详解

### 完整示例

```toml
# 登录认证
[login]
username = "admin"
password = "change_this_password"

# GitHub 账户
[accounts]
personal = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
work = "ghp_yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
opensource = "ghp_zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"
```

### 注意事项

- ✅ TOML 格式，注意缩进
- ✅ Token 以 `ghp_` 开头
- ✅ 账户名自定义
- ⚠️ 修改默认密码
- 🔒 Secrets 加密存储，安全可靠

## 📊 部署状态

### 成功部署的标志

1. ✅ 应用状态显示 **"Running"**
2. ✅ 可以访问应用 URL
3. ✅ 登录页面正常显示
4. ✅ 能够成功登录

### 常见问题

#### 问题 1: "This file does not exist"

**原因**：主文件路径配置错误

**解决**：
- 确保文件名是 `streamlit_app.py`
- 或在部署页面将 "Main file path" 改为 `streamlit_app.py`

#### 问题 2: "ModuleNotFoundError"

**原因**：依赖未正确安装

**解决**：
- 检查 `requirements.txt` 是否包含所有依赖
- 等待部署完成（可能需要几分钟）

#### 问题 3: "Invalid secrets format"

**原因**：Secrets 格式错误

**解决**：
- 确认使用 TOML 格式
- 检查缩进和语法
- 参考上面的完整示例

#### 问题 4: 登录失败

**原因**：Secrets 未配置或格式错误

**解决**：
- 确认 `[login]` 部分已配置
- 检查用户名和密码
- 保存后等待应用重启

## 🔄 更新应用

### 方式一：通过 Git Push

```bash
# 本地修改代码
git add .
git commit -m "Update features"
git push origin main

# Streamlit Cloud 自动检测并重新部署
```

### 方式二：通过 UI

1. 在 Streamlit Cloud 管理页面
2. 点击 **"Reboot app"**
3. 等待重启完成

### 更新 Secrets

1. 修改 Secrets 内容
2. 点击 **Save**
3. 应用自动重启

## 📈 性能优化

### 免费版限制

- 资源：1GB 内存，1 CPU 核心
- 适合：5-10 个账户
- 请求：合理使用 API

### 优化建议

1. **减少刷新频率**
   - 保活任务已优化为 60 秒刷新

2. **合理使用保活**
   - 不要同时保活太多 Codespace
   - 及时停止不需要的保活

3. **管理账户数量**
   - 免费版建议不超过 10 个账户

## 🎯 部署检查清单

部署前确认：

- [ ] 文件名已改为 `streamlit_app.py`
- [ ] `requirements.txt` 包含所有依赖
- [ ] 代码已推送到 GitHub
- [ ] 仓库是公开的或已授权给 Streamlit

部署后确认：

- [ ] 应用状态为 "Running"
- [ ] Secrets 已正确配置
- [ ] 登录功能正常
- [ ] 可以添加和管理账户
- [ ] Codespace 操作正常

## 📞 获取帮助

### Streamlit Cloud 文档

- [官方文档](https://docs.streamlit.io/streamlit-community-cloud)
- [部署指南](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)
- [Secrets 管理](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)

### 本项目文档

- [完整文档](README.md)
- [安全配置](SECURITY.md)
- [部署指南](DEPLOYMENT.md)

### 遇到问题？

- 查看 Streamlit Cloud 日志
- 检查 GitHub Actions（如果有）
- 提交 Issue 获取支持

---

**祝部署顺利！** 🚀

