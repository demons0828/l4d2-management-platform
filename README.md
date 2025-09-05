# L4D2 管理平台

一个基于Python FastAPI + Vue3的前后端分离L4D2服务器管理平台，提供完整的服务器管理、Mod下载、房间创建等功能。

## ✨ 功能特性

### 后端功能
- ✅ Steam登录认证
- ✅ L4D2服务器环境配置
- ✅ 多线程创意工坊内容下载
- ✅ Mod地图管理
- ✅ 搜索功能
- ✅ 房间创建和管理
- ✅ 游戏模式切换
- ✅ 地图切换
- ✅ Docker容器化部署

### 前端功能
- ✅ 移动端友好的响应式界面
- ✅ 现代化Vue3 + Element Plus UI
- ✅ 实时服务器状态监控
- ✅ 直观的管理界面

## 🚀 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- L4D2服务器（已安装在`/home/steam/l4d2_server`）

### Docker部署（推荐）

1. **克隆项目**
```bash
git clone <repository-url>
cd l4d2-management-platform
```

2. **运行部署脚本**
```bash
chmod +x docker/deploy.sh
./docker/deploy.sh
```

3. **访问应用**
- 前端界面: http://localhost:3000
- 后端API: http://localhost:8000
- Nginx代理: http://localhost

### 手动部署

#### 后端部署
```bash
cd backend
pip install -r requirements.txt
python run.py
```

#### 前端部署
```bash
cd frontend
npm install
npm run dev
```

## 📁 项目结构

```
l4d2-management-platform/
├── backend/                 # Python FastAPI后端
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置和认证
│   │   ├── models/         # 数据库模型
│   │   ├── schemas/        # Pydantic模式
│   │   ├── services/       # 业务逻辑服务
│   │   └── utils/          # 工具函数
│   ├── requirements.txt
│   └── run.py
├── frontend/                # Vue3前端
│   ├── src/
│   │   ├── api/            # API调用
│   │   ├── components/     # Vue组件
│   │   ├── views/          # 页面视图
│   │   ├── router/         # 路由配置
│   │   ├── stores/         # Pinia状态管理
│   │   └── utils/          # 工具函数
│   ├── package.json
│   └── vite.config.js
├── docker/                  # Docker配置
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── nginx.conf
│   └── deploy.sh
└── docker-compose.yml
```

## 🔧 配置说明

### 后端配置
编辑 `backend/.env` 文件：
```env
APP_NAME=L4D2 Management Platform
DEBUG=true
DATABASE_URL=sqlite:///./l4d2_manager.db
SECRET_KEY=your-secret-key-here
STEAM_API_KEY=your-steam-api-key
L4D2_SERVER_PATH=/home/steam/l4d2_server
STEAMCMD_PATH=/home/steam/steamcmd
```

### Steam配置
1. 使用管理脚本配置Steam账户：
```bash
/home/manage_steam_account.sh config
```

2. 测试登录：
```bash
/home/manage_steam_account.sh test
```

## 🎮 使用指南

### 服务器管理
1. 登录后进入"服务器管理"页面
2. 点击"添加服务器"创建新服务器
3. 使用控制按钮启动/停止/重启服务器
4. 实时查看服务器状态和信息

### Mod管理
1. 进入"Mod管理"页面
2. 输入创意工坊ID下载Mod
3. 查看下载进度和状态
4. 管理已安装的Mod

### 房间管理
1. 进入"房间管理"页面
2. 创建新的游戏房间
3. 设置房间参数（地图、模式等）
4. 邀请玩家加入房间

## 🔐 Steam登录

平台使用Steam OpenID进行用户认证：

1. 访问登录页面
2. 输入您的Steam ID（17位数字）
3. 点击登录完成认证

获取Steam ID方法：
- 访问 https://steamid.io/
- 输入Steam个人资料URL
- 复制显示的Steam64 ID

## 🐳 Docker管理

### 查看服务状态
```bash
docker-compose ps
```

### 查看日志
```bash
docker-compose logs -f
```

### 重启服务
```bash
docker-compose restart
```

### 停止服务
```bash
docker-compose down
```

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🆘 故障排除

### 常见问题

**Q: Steam登录失败**
A: 确保Steam账户配置正确，且API密钥已设置

**Q: 服务器启动失败**
A: 检查L4D2服务器文件是否正确安装在指定路径

**Q: Docker构建失败**
A: 确保所有依赖文件存在，且网络连接正常

**Q: 前端访问异常**
A: 检查Nginx配置和端口映射是否正确

### 日志查看
```bash
# 后端日志
docker-compose logs backend

# 前端日志
docker-compose logs frontend

# Nginx日志
docker-compose logs nginx
```

## 📞 联系我们

如有问题或建议，请提交Issue或Pull Request。

---

⭐ 如果这个项目对你有帮助，请给它一个星标！
