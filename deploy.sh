#!/bin/bash
# 一键部署脚本 - Canada 28 预测系统

set -e

echo "🚀 Canada 28 部署脚本"
echo "===================="
echo ""

# 检查是否为 root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用 sudo 运行此脚本"
    exit 1
fi

# 配置变量
PROJECT_DIR="/var/www/web-pcl28"
DOMAIN="${1:-yourdomain.com}"  # 第一个参数作为域名，默认 yourdomain.com

echo "📋 配置信息:"
echo "  项目目录: $PROJECT_DIR"
echo "  域名: $DOMAIN"
echo ""

read -p "确认继续? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# 1. 安装依赖
echo "📦 安装系统依赖..."
apt update
apt install -y python3 python3-pip python3-venv nginx supervisor git

# 2. 克隆或更新代码
if [ -d "$PROJECT_DIR" ]; then
    echo "📥 更新代码..."
    cd $PROJECT_DIR
    git pull || echo "⚠️  Git pull 失败，继续..."
else
    echo "📥 克隆代码..."
    mkdir -p $(dirname $PROJECT_DIR)
    git clone https://github.com/Zazak1/canada-28.git $PROJECT_DIR || {
        echo "❌ Git clone 失败，请手动上传代码到 $PROJECT_DIR"
        exit 1
    }
fi

# 3. 后端设置
echo "🔧 配置后端..."
cd $PROJECT_DIR/backend

# 创建虚拟环境
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# 创建环境变量文件（如果不存在）
if [ ! -f ".env" ]; then
    echo "📝 创建环境变量文件..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    cat > .env << EOF
SECRET_KEY=$SECRET_KEY
API_TOKEN=your-api-token-here
DATABASE_URL=sqlite:///pc28.db
POLL_INTERVAL=5
EOF
    echo "⚠️  请编辑 $PROJECT_DIR/backend/.env 设置 API_TOKEN"
fi

# 创建 Gunicorn 配置
cat > gunicorn.conf.py << 'EOF'
bind = "127.0.0.1:5000"
workers = 2
threads = 2
timeout = 120
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
EOF

mkdir -p /var/log/gunicorn
chown www-data:www-data /var/log/gunicorn

# 4. Supervisor 配置
echo "⚙️  配置 Supervisor..."
cat > /etc/supervisor/conf.d/pc28.conf << EOF
[program:pc28]
directory=$PROJECT_DIR/backend
command=$PROJECT_DIR/backend/venv/bin/gunicorn -c gunicorn.conf.py app:app
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/pc28/error.log
stdout_logfile=/var/log/pc28/output.log
environment=
    PATH="$PROJECT_DIR/backend/venv/bin"
EOF

mkdir -p /var/log/pc28
chown www-data:www-data /var/log/pc28

supervisorctl reread
supervisorctl update
supervisorctl start pc28 || supervisorctl restart pc28

# 5. 前端构建
echo "🎨 构建前端..."
cd $PROJECT_DIR/frontend

# 安装 Node.js（如果没有）
if ! command -v node &> /dev/null; then
    echo "📦 安装 Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
fi

# 修改 API 地址为相对路径
sed -i "s|const API_BASE = 'http://127.0.0.1:5000';|const API_BASE = '';|g" src/api.js

# 构建
npm install
npm run build

# 6. Nginx 配置
echo "🌐 配置 Nginx..."
cat > /etc/nginx/sites-available/pc28 << EOF
server {
    listen 80;
    server_name $DOMAIN;

    # 前端静态文件
    root $PROJECT_DIR/frontend/dist;
    index index.html;

    # 前端路由
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # 后端 API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
    }

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
}
EOF

# 启用站点
ln -sf /etc/nginx/sites-available/pc28 /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true

# 测试配置
nginx -t

# 重启 Nginx
systemctl reload nginx

echo ""
echo "✅ 部署完成！"
echo ""
echo "📝 下一步："
echo "  1. 编辑 $PROJECT_DIR/backend/.env 设置 API_TOKEN"
echo "  2. 重启服务: sudo supervisorctl restart pc28"
echo "  3. 配置 HTTPS: sudo certbot --nginx -d $DOMAIN"
echo ""
echo "🔍 查看日志:"
echo "  sudo tail -f /var/log/pc28/output.log"
echo ""
