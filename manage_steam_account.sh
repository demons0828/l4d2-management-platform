#!/bin/bash

# Steam账户管理脚本
# 用于管理L4D2服务器的Steam账户配置

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Steam配置
STEAM_CONFIG="/home/steam/.steam_config"

echo -e "${GREEN}Steam账户管理工具${NC}"
echo "===================="

# 显示当前配置状态
show_status() {
    echo -e "${BLUE}当前Steam账户配置状态：${NC}"
    if [[ -f $STEAM_CONFIG ]]; then
        source $STEAM_CONFIG
        echo "✓ 已配置账户：$STEAM_USERNAME"
        echo "  配置文件：$STEAM_CONFIG"
    else
        echo "✗ 未配置Steam账户"
        echo "  需要配置后才能下载创意工坊内容"
    fi
    echo ""
}

# 配置新账户
configure_account() {
    echo -e "${YELLOW}配置新的Steam账户${NC}"
    echo "注意：建议使用专门的Steam账户，不要使用您的主要账户"
    echo ""

    read -p "Steam用户名: " steam_username
    read -s -p "Steam密码: " steam_password
    echo ""

    # 备份旧配置
    if [[ -f $STEAM_CONFIG ]]; then
        cp $STEAM_CONFIG "${STEAM_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
        echo "旧配置已备份"
    fi

    # 保存新配置
    cat > $STEAM_CONFIG << EOF
STEAM_USERNAME="$steam_username"
STEAM_PASSWORD="$steam_password"
EOF
    chmod 600 $STEAM_CONFIG
    echo -e "${GREEN}Steam账户配置完成！${NC}"
    echo "账户：$steam_username"
}

# 删除账户配置
delete_account() {
    if [[ -f $STEAM_CONFIG ]]; then
        echo -e "${YELLOW}确认删除Steam账户配置？${NC}"
        read -p "输入 'yes' 确认删除: " confirm
        if [[ $confirm == "yes" ]]; then
            rm -f $STEAM_CONFIG
            echo -e "${GREEN}Steam账户配置已删除${NC}"
        else
            echo "操作已取消"
        fi
    else
        echo -e "${RED}未找到Steam账户配置${NC}"
    fi
}

# 测试账户登录
test_login() {
    if [[ ! -f $STEAM_CONFIG ]]; then
        echo -e "${RED}请先配置Steam账户${NC}"
        return 1
    fi

    source $STEAM_CONFIG
    echo -e "${YELLOW}测试Steam账户登录...${NC}"
    echo "账户：$STEAM_USERNAME"

    cd /home/steam/steamcmd
    ./steamcmd.sh +login $STEAM_USERNAME $STEAM_PASSWORD +quit

    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}Steam账户登录测试成功！${NC}"
    else
        echo -e "${RED}Steam账户登录测试失败${NC}"
        echo "请检查用户名和密码是否正确"
    fi
}

# 显示帮助
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项："
    echo "  status    - 显示当前账户配置状态"
    echo "  config    - 配置新的Steam账户"
    echo "  delete    - 删除当前账户配置"
    echo "  test      - 测试账户登录"
    echo "  help      - 显示此帮助信息"
    echo ""
    echo "示例："
    echo "  $0 status     # 查看配置状态"
    echo "  $0 config     # 配置账户"
    echo "  $0 test       # 测试登录"
}

# 主逻辑
case "$1" in
    status)
        show_status
        ;;
    config)
        configure_account
        ;;
    delete)
        delete_account
        ;;
    test)
        test_login
        ;;
    help|"")
        show_help
        ;;
    *)
        echo -e "${RED}无效选项: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
