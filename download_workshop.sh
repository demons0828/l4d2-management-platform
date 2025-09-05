#!/bin/bash

# L4D2 创意工坊下载脚本
# 用于下载和管理 L4D2 服务器的创意工坊内容

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Steam配置
STEAM_CONFIG="/home/steam/.steam_config"

echo -e "${GREEN}L4D2 创意工坊下载工具${NC}"
echo "========================"

# 检查Steam配置
check_steam_config() {
    if [[ ! -f $STEAM_CONFIG ]]; then
        echo -e "${YELLOW}首次使用需要配置Steam账户信息${NC}"
        echo ""
        echo -e "${BLUE}建议使用账户管理脚本进行配置：${NC}"
        echo "/home/manage_steam_account.sh config"
        echo ""
        echo "或者现在直接配置："

        read -p "Steam用户名: " steam_username
        read -s -p "Steam密码: " steam_password
        echo ""

        # 保存配置
        cat > $STEAM_CONFIG << EOF
STEAM_USERNAME="$steam_username"
STEAM_PASSWORD="$steam_password"
EOF
        chmod 600 $STEAM_CONFIG
        echo -e "${GREEN}Steam账户信息已保存${NC}"
        echo ""
    fi

    # 读取配置
    source $STEAM_CONFIG
}

# 检查参数
if [[ $# -eq 0 ]]; then
    echo "用法: $0 <创意工坊ID> [创意工坊ID2] [创意工坊ID3] ..."
    echo ""
    echo "示例:"
    echo "  $0 123456789                    # 下载单个物品"
    echo "  $0 123456789 987654321 111111111 # 下载多个物品"
    echo ""
    echo "常用创意工坊ID:"
    echo "  SourceMod:           811732"
    echo "  MetaMod:            524217"
    echo "  Admin Menu:         409356"
    echo "  Basic Chat:         409354"
    echo "  L4D2 Toolkit:       513531"
    echo "  Server Redirect:    409362"
    echo ""
    echo "在创意工坊页面找到物品ID："
    echo "https://steamcommunity.com/app/550/workshop/"
    echo "物品ID在URL末尾，例如：.../?id=123456789"
    echo ""
    echo "Steam账户管理："
    echo "  /home/manage_steam_account.sh status   # 查看账户状态"
    echo "  /home/manage_steam_account.sh config   # 配置账户"
    echo "  /home/manage_steam_account.sh test     # 测试登录"
    echo "  /home/manage_steam_account.sh delete   # 删除配置"
    exit 1
fi

# 检查SteamCMD是否存在
if [[ ! -f /home/steam/steamcmd/steamcmd.sh ]]; then
    echo -e "${RED}错误：未找到SteamCMD，请先运行部署脚本${NC}"
    exit 1
fi

# 检查服务器目录是否存在
if [[ ! -d /home/steam/l4d2_server ]]; then
    echo -e "${RED}错误：未找到L4D2服务器目录，请先运行部署脚本${NC}"
    exit 1
fi

# 检查并配置Steam账户
check_steam_config

echo -e "${YELLOW}开始下载创意工坊内容...${NC}"
echo -e "${BLUE}使用Steam账户：$STEAM_USERNAME${NC}"

# 构建下载命令
workshop_cmd="+login $STEAM_USERNAME $STEAM_PASSWORD"
for workshop_id in "$@"; do
    if [[ $workshop_id =~ ^[0-9]+$ ]]; then
        workshop_cmd="$workshop_cmd +workshop_download_item 550 $workshop_id"
        echo "添加下载任务：ID $workshop_id"
    else
        echo -e "${RED}警告：无效的创意工坊ID '$workshop_id'，跳过${NC}"
    fi
done
workshop_cmd="$workshop_cmd +quit"

# 执行下载
cd /home/steam/steamcmd
./steamcmd.sh $workshop_cmd

if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}下载完成！${NC}"
    echo ""
    echo "下载的文件位于："
    echo "/home/steam/steam/steamapps/workshop/content/550/"
    echo ""
    echo "要使用这些文件，请将它们复制到服务器目录："
    echo "cp -r /home/steam/steam/steamapps/workshop/content/550/* /home/steam/l4d2_server/left4dead2/"
    echo ""
    echo "复制文件到服务器目录..."
    for workshop_id in "$@"; do
        if [[ $workshop_id =~ ^[0-9]+$ ]]; then
            workshop_dir="/home/steam/steam/steamapps/workshop/content/550/$workshop_id"
            if [[ -d $workshop_dir ]]; then
                cp -r "$workshop_dir"/* /home/steam/l4d2_server/left4dead2/ 2>/dev/null
                echo "已复制 ID $workshop_id 的内容到服务器目录"
            fi
        fi
    done

    echo ""
    echo -e "${GREEN}所有文件已复制完成！${NC}"
    echo "请重启服务器以应用更改："
    echo "/home/steam/manage_server.sh restart"
else
    echo -e "${RED}下载过程中出现错误${NC}"
    exit 1
fi
