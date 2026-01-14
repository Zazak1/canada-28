# Canada 28 预测系统

实时开奖数据展示和 AI 预测系统，支持多种算法独立统计和历史对比。

## ✨ 功能特性

- 🎯 **实时开奖数据**：每 5 秒自动同步最新开奖结果
- ⏱️ **倒计时显示**：实时显示下期开奖倒计时
- 🤖 **多算法预测**：支持三种算法独立预测和统计
- 📊 **历史对比**：每个算法独立保存预测记录，基于最近 100 期数据统计
- 🎨 **现代化 UI**：响应式设计，Tailwind CSS 样式

## 🚀 快速开始

### 本地开发

```bash
# 后端
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py

# 前端（新终端）
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

### 部署到服务器

#### 方式一：一键部署脚本（推荐）

```bash
# 上传代码到服务器后
sudo ./deploy.sh yourdomain.com
```

#### 方式二：手动部署

详细步骤请查看 [DEPLOY.md](./DEPLOY.md)

## 📁 项目结构

```
web-pcl28/
├── backend/              # Flask 后端
│   ├── app.py           # 主应用
│   ├── models.py        # 数据模型
│   ├── config.py        # 配置
│   ├── services/        # 业务逻辑
│   │   ├── fetcher.py   # 数据抓取
│   │   ├── predictor.py # 预测服务
│   │   └── algorithms/  # 算法模块
│   └── requirements.txt
├── frontend/            # React 前端
│   ├── src/
│   │   ├── components/  # React 组件
│   │   └── api.js       # API 调用
│   └── package.json
└── DEPLOY.md            # 部署文档
```

## 🔧 配置说明

### 后端环境变量

创建 `backend/.env` 文件：

```bash
SECRET_KEY=your-secret-key
API_TOKEN=your-api-token
DATABASE_URL=sqlite:///pc28.db
POLL_INTERVAL=5
```

### 前端 API 地址

生产环境修改 `frontend/src/api.js`：

```javascript
const API_BASE = '';  // 相对路径（前后端同域）
// 或
const API_BASE = 'https://yourdomain.com';  // 完整域名
```

## 📊 API 端点

| 端点 | 说明 |
|------|------|
| `GET /api/status` | 系统状态 |
| `GET /api/latest` | 最新开奖和倒计时 |
| `GET /api/prediction?algorithm=algo1` | 获取预测 |
| `GET /api/algorithms` | 算法列表 |
| `GET /api/algorithms/stats` | 所有算法统计 |
| `GET /api/algorithm/{id}/history` | 算法历史记录 |

## 🛠️ 技术栈

- **后端**: Flask + SQLAlchemy + APScheduler
- **前端**: React + Vite + Tailwind CSS
- **数据库**: SQLite（可升级 PostgreSQL）

## 📝 许可证

MIT License
