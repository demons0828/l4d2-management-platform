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

# 区域设置函数
setup_region_config() {
    echo -e "${BLUE}配置下载区域设置${NC}"
    echo "选择离你物理距离最近的区域可以改善下载速度："
    echo ""
    echo "1) Shanghai    (上海)"
    echo "2) Beijing     (北京)"
    echo "3) Hongkong    (香港)"
    echo "4) Tokyo       (东京)"
    echo "5) Singapore   (新加坡)"
    echo "6) Auto        (自动选择)"
    echo ""

    while true; do
        read -p "请选择区域 (1-6): " region_choice

        case $region_choice in
            1) STEAM_REGION="china"; break ;;
            2) STEAM_REGION="china"; break ;;
            3) STEAM_REGION="china"; break ;;
            4) STEAM_REGION="japan"; break ;;
            5) STEAM_REGION="singapore"; break ;;
            6) STEAM_REGION="auto"; break ;;
            *) echo -e "${RED}无效选择，请重新选择${NC}" ;;
        esac
    done

    # 保存区域配置
    if [[ -f $STEAM_CONFIG ]]; then
        # 读取现有配置
        source $STEAM_CONFIG
    fi

    # 更新或添加区域配置
    cat > $STEAM_CONFIG << EOF
STEAM_USERNAME="$STEAM_USERNAME"
STEAM_PASSWORD="$STEAM_PASSWORD"
STEAM_REGION="$STEAM_REGION"
EOF
    chmod 600 $STEAM_CONFIG
    echo -e "${GREEN}区域设置已保存：$STEAM_REGION${NC}"
    echo ""
}

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
STEAM_REGION="china"
EOF
        chmod 600 $STEAM_CONFIG
        echo -e "${GREEN}Steam账户信息已保存${NC}"
        echo -e "${GREEN}默认区域设置为：china${NC}"
        echo ""
    fi

    # 读取配置
    source $STEAM_CONFIG

    # 检查是否需要配置区域
    if [[ -z "$STEAM_REGION" ]]; then
        echo -e "${YELLOW}未找到区域设置，请配置下载区域${NC}"
        setup_region_config
        source $STEAM_CONFIG
    fi
}

# 处理命令行参数
REGION_SWITCH=""
WORKSHOP_IDS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --region)
            if [[ -n "$2" && ! "$2" =~ ^-- ]]; then
                REGION_SWITCH="$2"
                shift 2
            else
                echo -e "${RED}错误：--region 参数需要指定区域值${NC}"
                echo "可用区域：china, japan, singapore, auto"
                exit 1
            fi
            ;;
        --config-region)
            setup_region_config
            source $STEAM_CONFIG
            shift
            ;;
        *)
            # 检查是否为数字（创意工坊ID）
            if [[ $1 =~ ^[0-9]+$ ]]; then
                WORKSHOP_IDS="$WORKSHOP_IDS $1"
            else
                echo -e "${RED}错误：无效参数 '$1'${NC}"
                echo ""
                echo "用法: $0 <创意工坊ID> [创意工坊ID2] [创意工坊ID3] ..."
                echo ""
                echo "选项："
                echo "  --region <区域>        临时切换下载区域"
                echo "  --config-region        配置默认下载区域"
                echo ""
                echo "可用区域：china, japan, singapore, auto"
                echo ""
                echo "示例:"
                echo "  $0 123456789                           # 下载单个物品"
                echo "  $0 123456789 987654321 111111111        # 下载多个物品"
                echo "  $0 --region china 123456789             # 使用中国区域下载"
                echo "  $0 --config-region                      # 配置默认区域"
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
            shift
            ;;
    esac
done

# 检查是否提供了创意工坊ID
if [[ -z "$WORKSHOP_IDS" ]]; then
    echo "用法: $0 <创意工坊ID> [创意工坊ID2] [创意工坊ID3] ..."
    echo ""
    echo "选项："
    echo "  --region <区域>        临时切换下载区域"
    echo "  --config-region        配置默认下载区域"
    echo ""
    echo "可用区域：china, japan, singapore, auto"
    echo ""
    echo "示例:"
    echo "  $0 123456789                           # 下载单个物品"
    echo "  $0 123456789 987654321 111111111        # 下载多个物品"
    echo "  $0 --region china 123456789             # 使用中国区域下载"
    echo "  $0 --config-region                      # 配置默认区域"
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

# 确定使用的区域
if [[ -n "$REGION_SWITCH" ]]; then
    CURRENT_REGION="$REGION_SWITCH"
    echo -e "${BLUE}临时使用区域：$CURRENT_REGION${NC}"
else
    CURRENT_REGION="$STEAM_REGION"
    echo -e "${BLUE}使用配置区域：$CURRENT_REGION${NC}"
fi

# 构建下载命令
if [[ "$CURRENT_REGION" == "auto" ]]; then
    workshop_cmd="+login $STEAM_USERNAME $STEAM_PASSWORD"
else
    workshop_cmd="@sSteamCmdForceRegionType $CURRENT_REGION +login $STEAM_USERNAME $STEAM_PASSWORD"
fi

for workshop_id in $WORKSHOP_IDS; do
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
    for workshop_id in $WORKSHOP_IDS; do
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
