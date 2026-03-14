# 部署指南

## 架构概述

- **前端**: 纯HTML/JavaScript (部署到 Netlify)
- **后端**: FastAPI (部署到 Railway)
- **数据库**: TiDB Cloud

---

## 第一步：准备 GitHub 仓库

1. 在 GitHub 上创建一个新的仓库
2. 将 dataflow diagram 项目代码推送到该仓库

---

## 第二步：部署前端到 Netlify

### 1. 登录 Netlify

访问 https://netlify.com 并使用 GitHub 账号登录。

### 2. 导入项目

1. 点击 "Add new site" → "Deploy with Git"
2. 选择 "GitHub"
3. 授权 Netlify 访问您的 GitHub 仓库
4. 选择 dataflow diagram 仓库

### 3. 配置部署设置

在 "Site settings" 页面：

- **Base directory**: `frontend-prototype`
- **Build command**: `echo 'Build completed'`
- **Publish directory**: `.`

### 4. 配置环境变量

在 "Site settings" → "Environment variables" 中添加：

```
NEXT_PUBLIC_API_URL=你的Railway后端URL (稍后获取)
```

### 5. 部署

点击 "Deploy site" 等待部署完成。

---

## 第三步：部署后端到 Railway

### 1. 登录 Railway

访问 https://railway.app 并使用 GitHub 账号登录。

### 2. 创建新项目

1. 点击 "New Project"
2. 选择 "Deploy from repo"
3. 选择 dataflow diagram 仓库

### 3. 配置环境变量

在 Railway 项目设置中添加以下环境变量：

```
DB_HOST=你的TiDB主机地址
DB_PORT=4000
DB_USER=你的TiDB用户名
DB_PASSWORD=你的TiDB密码
DB_NAME=你的数据库名
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=Admin@123456
CORS_ALLOW_ORIGINS=你的Netlify前端URL,http://localhost:8088,http://127.0.0.1:8088,http://localhost:5500,http://127.0.0.1:5500,http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000
```

### 4. 部署

Railway 会自动检测 `Dockerfile` 并开始部署。

### 5. 获取后端 URL

部署完成后，Railway 会提供一个 URL，例如：`https://dataflow-backend.up.railway.app`

---

## 第四步：完成配置

### 1. 更新 Netlify 环境变量

回到 Netlify 项目设置，更新 `NEXT_PUBLIC_API_URL` 为你的 Railway 后端 URL。

### 2. 重新部署 Netlify

触发一次新的部署以使环境变量生效。

---

## 本地开发

### 前端开发

```bash
cd frontend-prototype
# 使用本地服务器打开 index.html
# 例如：使用 VS Code 的 Live Server 扩展
```

### 后端开发

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn import_status_api:app --host 0.0.0.0 --port 8000 --reload
```

### 环境变量

创建 `.env` 文件（不要提交到 Git）：

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=dataflow_digram
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=Admin@123456
CORS_ALLOW_ORIGINS=http://localhost:8088,http://127.0.0.1:8088,http://localhost:5500,http://127.0.0.1:5500,http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000
```

---

## 安全注意事项

1. **永远不要将 `.env` 文件提交到 Git**
2. 使用强密码和随机生成的密钥
3. 定期轮换密钥
4. 在生产环境中启用 HTTPS

---

## 故障排除

### 前端无法连接后端

- 检查 `NEXT_PUBLIC_API_URL` 是否正确
- 确保后端服务正在运行
- 检查 CORS 配置

### 后端无法连接数据库

- 检查数据库环境变量
- 确认数据库服务可访问
- 验证用户名和密码

---

## 技术栈

- **前端**: 纯HTML/JavaScript + CSS
- **后端**: FastAPI
- **数据库**: TiDB (MySQL兼容)
- **部署**: Netlify (前端) + Railway (后端)
