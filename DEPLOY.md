# 部署指南

## 📋 部署前检查清单

### 1. 安全相关（重要！）

| 项目 | 说明 | 操作 |
|------|------|------|
| **API Token** | `config.py` 中的 `API_TOKEN` 是敏感信息 | 改用环境变量，不要提交到 Git |
| **Debug 模式** | 生产环境必须关闭 debug | 设置 `debug=False` |
| **Secret Key** | Flask 需要安全的密钥 | 添加 `SECRET_KEY` 配置 |
| **CORS** | 限制跨域来源 | 配置具体域名而非 `*` |

### 2. 需要修改的文件

#### 后端 `backend/config.py` - 添加生产配置

```python
import os

class Config:
    # 安全密钥（生产环境必须设置）
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this'
    
    # 数据库（生产环境建议用 PostgreSQL/MySQL）
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///pc28.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 调度器
    SCHEDULER_API_ENABLED = True
    POLL_INTERVAL = int(os.environ.get('POLL_INTERVAL', 15))
    
    # 外部 API（敏感信息用环境变量）
    API_BASE_URL = os.environ.get('API_BASE_URL', 'http://hanxin28.com/api/api.php')
    API_TOKEN = os.environ.get('API_TOKEN')  # 必须通过环境变量设置
    GAME_TYPE = os.environ.get('GAME_TYPE', 'jnd28')
    HISTORY_FETCH_LIMIT = int(os.environ.get('HISTORY_FETCH_LIMIT', 50))
    API_TIMEOUT = int(os.environ.get('API_TIMEOUT', 10))
```

#### 前端 `frontend/src/api.js` - 修改 API 地址

```javascript
// 开发环境
// const API_BASE = 'http://127.0.0.1:5000';

// 生产环境（改为你的域名）
const API_BASE = 'https://yourdomain.com/api';
// 或者使用相对路径（如果前后端同域）
// const API_BASE = '/api';
```

---

## 🚀 部署步骤

### 方案一：传统部署（推荐新手）

#### 1. 服务器环境准备

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx supervisor

# CentOS
sudo yum install python3 python3-pip nginx supervisor
```

#### 2. 上传代码

```bash
# 在本地
scp -r web-pcl28 user@your-server:/var/www/

# 或使用 Git
git clone your-repo /var/www/web-pcl28
```

#### 3. 后端设置

```bash
cd /var/www/web-pcl28/backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install gunicorn  # 生产级 WSGI 服务器

# 创建环境变量文件
cat > .env << 'EOF'
SECRET_KEY=your-very-long-random-secret-key-here
API_TOKEN=your-api-token-here
DATABASE_URL=sqlite:///pc28.db
EOF
```

#### 4. 创建 Gunicorn 配置

```bash
cat > /var/www/web-pcl28/backend/gunicorn.conf.py << 'EOF'
bind = "127.0.0.1:5000"
workers = 2
threads = 2
timeout = 120
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
EOF

sudo mkdir -p /var/log/gunicorn
sudo chown www-data:www-data /var/log/gunicorn
```

#### 5. 创建 Supervisor 配置

```bash
sudo cat > /etc/supervisor/conf.d/pc28.conf << 'EOF'
[program:pc28]
directory=/var/www/web-pcl28/backend
command=/var/www/web-pcl28/backend/venv/bin/gunicorn -c gunicorn.conf.py app:app
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/pc28/error.log
stdout_logfile=/var/log/pc28/output.log
environment=
    SECRET_KEY="your-secret-key",
    API_TOKEN="your-api-token"
EOF

sudo mkdir -p /var/log/pc28
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start pc28
```

#### 6. 构建前端

```bash
cd /var/www/web-pcl28/frontend

# 安装 Node.js（如果没有）
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# 构建
npm install
npm run build
```

#### 7. 配置 Nginx

```bash
sudo cat > /etc/nginx/sites-available/pc28 << 'EOF'
server {
    listen 80;
    server_name yourdomain.com;  # 改为你的域名

    # 前端静态文件
    root /var/www/web-pcl28/frontend/dist;
    index index.html;

    # 前端路由
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/pc28 /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 8. 配置 HTTPS（强烈推荐）

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d yourdomain.com

# 自动续期
sudo certbot renew --dry-run
```

---

### 方案二：Docker 部署（推荐生产环境）

#### 1. 创建 Dockerfile

**后端 `backend/Dockerfile`**：
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "2", "app:app"]
```

**前端 `frontend/Dockerfile`**：
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

#### 2. 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    restart: always
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - API_TOKEN=${API_TOKEN}
      - DATABASE_URL=sqlite:///data/pc28.db
    volumes:
      - ./data:/app/data

  frontend:
    build: ./frontend
    restart: always
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
```

#### 3. 启动

```bash
docker-compose up -d
```

---

## ⚠️ 重要注意事项

### 安全
1. **永远不要**把 `API_TOKEN` 提交到 Git
2. 生产环境**必须关闭** `debug=True`
3. 使用 HTTPS
4. 定期备份数据库

### 性能
1. SQLite 适合小规模，大规模建议换 PostgreSQL
2. 考虑添加 Redis 缓存热点数据
3. 静态文件开启 Gzip 压缩

### 监控
1. 设置日志轮转，防止磁盘爆满
2. 监控服务状态（可用 uptimerobot 等）
3. 监控外部 API 调用是否正常

### 前端 API 地址
部署后需要修改 `frontend/src/api.js`：

```javascript
// 方案1：使用完整域名
const API_BASE = 'https://yourdomain.com';

// 方案2：使用相对路径（推荐，前后端同域时）
const API_BASE = '';
```

---

## 📁 目录结构建议

```
/var/www/web-pcl28/
├── backend/
│   ├── venv/
│   ├── instance/
│   │   └── pc28.db      # 数据库文件
│   ├── app.py
│   ├── .env             # 环境变量（不要提交 Git）
│   └── ...
├── frontend/
│   ├── dist/            # 构建产物
│   └── ...
└── data/                # 持久化数据（Docker 方案）
```

---

## 🔧 常用运维命令

```bash
# 查看后端日志
sudo tail -f /var/log/pc28/output.log

# 重启后端
sudo supervisorctl restart pc28

# 重启 Nginx
sudo systemctl reload nginx

# 查看服务状态
sudo supervisorctl status
```
