# 📦 部署指南

本指南介绍如何在不同环境中部署 GitHub Codespaces Manager。

## 🏠 本地部署

### 基础部署

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd codespace-manager

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置账户（可选）
cp accounts.json.example accounts.json
# 编辑 accounts.json 添加你的 token

# 4. 运行
streamlit run streamlit_app.py
```

### 使用虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行
streamlit run streamlit_app.py
```

### Docker 部署（可选）

创建 `Dockerfile`：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

构建和运行：

```bash
# 构建镜像
docker build -t codespace-manager .

# 运行容器
docker run -p 8501:8501 -v $(pwd)/accounts.json:/app/accounts.json codespace-manager
```

## ☁️ Streamlit Cloud 部署

### 方式一：通过 Web 界面

1. **准备代码**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo>
   git push -u origin main
   ```

2. **部署应用**
   - 访问 [share.streamlit.io](https://share.streamlit.io/)
   - 点击 "New app"
   - 连接 GitHub 账户
   - 选择仓库和分支
   - 主文件选择 `streamlit_app.py`（或留空，自动识别）
   - 点击 "Deploy"

3. **配置 Secrets**
   - 等待应用部署完成
   - 点击 "Settings" → "Secrets"
   - 添加账户配置：
   
   ```toml
   [accounts]
   account1 = "ghp_your_token_1"
   account2 = "ghp_your_token_2"
   ```
   
   - 点击 "Save"
   - 应用会自动重启

4. **完成**
   - 访问你的应用 URL
   - 开始使用！

### 方式二：通过 CLI

```bash
# 安装 Streamlit CLI
pip install streamlit

# 登录
streamlit login

# 部署
streamlit deploy streamlit_app.py
```

### Secrets 配置详解

#### 基础配置

```toml
[accounts]
# 格式: 账户名 = "token"
my_personal = "ghp_xxxxxxxxxxxx"
my_work = "ghp_xxxxxxxxxxxx"
```

#### 多账户配置示例

```toml
[accounts]
# 个人账户
personal = "ghp_personal_token_here"

# 工作账户
work_frontend = "ghp_work_token_here"
work_backend = "ghp_work_token_here"

# 开源项目
opensource = "ghp_opensource_token_here"

# 团队账户
team_devops = "ghp_team_token_here"
team_qa = "ghp_team_token_here"
```

## 🔧 环境配置

### 本地开发配置

#### 选项 1: accounts.json（推荐）

```json
{
  "account1": "ghp_token1",
  "account2": "ghp_token2"
}
```

#### 选项 2: .env 文件（已弃用，但仍支持）

```env
GITHUB_TOKEN=ghp_your_single_token
```

### Streamlit Cloud 配置

只需要在 Secrets 中配置，无需其他文件。

### 混合配置

- **Streamlit Secrets**：云端部署使用，安全加密
- **accounts.json**：本地开发使用，gitignore 已排除
- **应用内添加**：临时测试使用，保存到 accounts.json

## 🌐 域名配置

### 使用 Streamlit 默认域名

```
https://your-app-name.streamlit.app
```

### 自定义域名（Streamlit Cloud）

1. 升级到 Streamlit Cloud Teams/Enterprise
2. 在设置中配置自定义域名
3. 添加 DNS CNAME 记录
4. 等待 SSL 证书生成

### 使用反向代理（自托管）

#### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔐 安全最佳实践

### 1. Token 管理

- ✅ 使用 Streamlit Secrets（云端）
- ✅ 使用 accounts.json（本地，不提交）
- ✅ 定期轮换 token
- ❌ 不要硬编码 token
- ❌ 不要提交 token 到 Git

### 2. 权限控制

- 只授予 `codespace` 权限
- 为不同用途创建不同的 token
- 使用有过期时间的 token

### 3. 访问控制

Streamlit Cloud 自动提供：
- HTTPS 加密
- 身份验证（可选）
- 访问日志

### 4. 备份

定期备份 `accounts.json`（本地）或导出 Secrets 配置。

## 📊 性能优化

### 1. 缓存配置

应用已内置缓存机制，session state 缓存：
- 账户信息
- Manager 实例
- 用户信息

### 2. 请求优化

- 避免频繁刷新
- 使用手动刷新按钮
- 合理设置刷新间隔

### 3. 资源限制

Streamlit Cloud 免费版限制：
- 1GB 内存
- 1 CPU 核心
- 适合管理 5-10 个账户

## 🔄 更新和维护

### 更新应用（Streamlit Cloud）

```bash
# 本地更新代码
git pull origin main

# 推送到 GitHub
git add .
git commit -m "Update"
git push

# Streamlit Cloud 会自动检测并重新部署
```

### 更新依赖

```bash
# 更新 requirements.txt
pip list --outdated
pip install --upgrade streamlit requests

# 导出新依赖
pip freeze > requirements.txt
```

## 🐛 故障排查

### 应用无法启动

1. 检查 requirements.txt 是否完整
2. 查看 Streamlit Cloud 日志
3. 验证 Python 版本（3.8+）

### Token 无效

1. 检查 token 格式（以 `ghp_` 开头）
2. 验证 token 权限（包含 `codespace`）
3. 检查 token 是否过期

### Secrets 不生效

1. 确认 Secrets 格式正确（TOML）
2. 保存后等待应用重启
3. 检查是否有拼写错误

### 性能问题

1. 减少账户数量
2. 使用手动刷新替代自动刷新
3. 考虑升级 Streamlit Cloud 计划

## 📞 支持

- 查看 [README.md](README.md) 了解更多信息
- 查看 [QUICKSTART.md](QUICKSTART.md) 快速上手
- 提交 Issue 反馈问题

---

🚀 祝部署顺利！

