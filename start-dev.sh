#!/bin/bash

# L4D2管理平台开发环境启动脚本

echo "🚀 启动L4D2管理平台开发环境..."

# 检查Python和Node.js
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js未安装"
    exit 1
fi

# 启动后端
echo "🔧 启动后端服务..."
cd backend
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

echo "🌐 后端服务启动在 http://localhost:8000"
python run.py &
BACKEND_PID=$!

cd ..

# 启动前端
echo "🎨 启动前端服务..."
cd frontend
npm install
echo "🌐 前端服务启动在 http://localhost:3000"
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "✅ 开发环境已启动！"
echo "   前端: http://localhost:3000"
echo "   后端: http://localhost:8000"
echo ""
echo "🛑 按 Ctrl+C 停止服务"

# 等待用户中断
trap "echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
