#!/bin/bash

# L4D2 服务端下载脚本 - 使用上海加速
# 使用Steam账户下载Left 4 Dead 2 专用服务器

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}L4D2 服务端下载工具 - 上海加速${NC}"
echo "=================================="

# Steam配置
STEAM_CONFIG="/home/steam/.steam_config"

# 检查Steam配置
if [[ ! -f $STEAM_CONFIG ]]; then
    echo -e "${RED}错误：未找到Steam账户配置${NC}"
    echo "请先运行Steam账户配置脚本"
    exit 1
fi

# 读取配置
source $STEAM_CONFIG

echo -e "${BLUE}使用Steam账户：$STEAM_USERNAME${NC}"
echo -e "${BLUE}下载区域：上海 (China)${NC}"
echo ""

# 检查SteamCMD是否存在
if [[ ! -f /home/steam/steamcmd/steamcmd.sh ]]; then
    echo -e "${RED}错误：未找到SteamCMD${NC}"
    echo "请先运行部署脚本安装SteamCMD"
    exit 1
fi

# 创建L4D2服务器目录
echo -e "${YELLOW}准备下载目录...${NC}"
sudo -u steam mkdir -p /home/steam/l4d2_server

# 开始下载L4D2服务端
echo -e "${YELLOW}开始下载L4D2服务端文件...${NC}"
echo -e "${BLUE}使用上海加速节点${NC}"
echo "这可能需要一些时间，请耐心等待..."
echo ""

cd /home/steam/steamcmd

# 使用上海加速下载L4D2服务端
sudo -u steam ./steamcmd.sh \
    @sSteamCmdForceRegionType china \
    +login $STEAM_USERNAME $STEAM_PASSWORD \
    +force_install_dir /home/steam/l4d2_server \
    +app_update 222860 validate \
    +quit

# 检查下载结果
if [[ $? -eq 0 ]]; then
    echo ""
    echo -e "${GREEN}L4D2服务端下载完成！${NC}"
    echo ""
    echo "安装目录：/home/steam/l4d2_server"
    echo "游戏目录：/home/steam/l4d2_server/left4dead2"
    echo ""
    echo -e "${BLUE}下载统计信息：${NC}"
    du -sh /home/steam/l4d2_server
    echo ""
    echo -e "${GREEN}接下来您可以：${NC}"
    echo "1. 配置服务器：编辑 /home/steam/l4d2_server/left4dead2/cfg/server.cfg"
    echo "2. 启动服务器：/home/steam/manage_server.sh start"
    echo "3. 下载创意工坊内容：/home/download_workshop.sh <workshop_id>"
else
    echo ""
    echo -e "${RED}下载过程中出现错误${NC}"
    echo "请检查："
    echo "1. Steam账户信息是否正确"
    echo "2. 网络连接是否正常"
    echo "3. Steam服务是否可用"
    exit 1
fi
