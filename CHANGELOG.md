# 更新日志

## [1.1.0] - 2025-10-26

### 🔐 新功能

1. **添加登录认证**
   - 需要用户名和密码才能访问应用
   - 登录凭证存储在 Streamlit Secrets
   - 默认凭证：username=`admin`, password=`admin`
   - 支持本地和云端环境

2. **数据持久化说明**
   - 本地：使用 `accounts.json` 文件
   - 云端：使用 Streamlit Secrets
   - 重启后自动加载所有账户

### 🔒 安全改进

1. **移除删除 Codespace 功能**
   - 为了安全，不再允许在应用中删除 Codespace
   - 请在 GitHub 网页端删除

2. **增强安全文档**
   - 添加 `SECURITY.md` 详细说明安全配置
   - 更新 README 包含存储位置说明
   - 更新 secrets 示例文件

### 📝 文档更新

- 添加登录配置说明
- 添加数据存储位置说明
- 添加 SECURITY.md 文档
- 更新快速开始指南

---

## [1.0.1] - 2025-10-26

### 🐛 Bug 修复

1. **修复 Windows pyarrow DLL 错误**
   - 移除了 pandas 依赖
   - 将 `st.dataframe()` 改为 `st.table()`
   - 解决了 "DLL load failed while importing lib" 错误

2. **修复删除 Codespace 功能**
   - 添加了删除确认机制
   - 使用 session state 跟踪确认状态
   - 点击 🗑️ 后显示 ⚠️ Confirm 按钮
   - 防止误删除操作

### 🎯 改进

- 减少了依赖包大小（移除 pandas）
- 改进了删除操作的用户体验
- 更好的错误处理

---

## [1.0.0] - 2025-10-26

### ✨ 初始版本

- 多账户支持
- Codespace 管理（列出、启动、停止、删除、创建）
- 本地和 Streamlit Cloud 双环境支持
- 现代化 UI 界面
- 完整的文档


