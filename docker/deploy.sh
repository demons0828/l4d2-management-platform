#!/bin/bash

# L4D2管理平台Docker部署脚本

set -e

echo "🚀 开始部署L4D2管理平台..."

# 检查Docker和docker-compose是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose未安装，请先安装docker-compose"
    exit 1
fi

# 创建数据目录
echo "📁 创建数据目录..."
mkdir -p data

# 检查Steam路径是否存在
if [ ! -d "/home/steam" ]; then
    echo "⚠️  警告: /home/steam 路径不存在"
    echo "请确保L4D2服务器已正确安装在 /home/steam/l4d2_server"
fi

# 构建并启动服务
echo "🏗️  构建并启动服务..."
docker-compose up -d --build

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 显示访问信息
echo ""
echo "✅ 部署完成！"
echo ""
echo "🌐 服务访问地址:"
echo "   前端: http://localhost:3000"
echo "   后端API: http://localhost:8000"
echo "   Nginx代理: http://localhost"
echo ""
echo "📊 查看日志:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 停止服务:"
echo "   docker-compose down"
echo ""
echo "🔄 重启服务:"
echo "   docker-compose restart"
