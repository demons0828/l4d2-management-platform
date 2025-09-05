#!/bin/bash

# L4D2 服务器部署脚本
# 用于在 Linux 系统上自动部署 Left 4 Dead 2 专用服务器

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# # 检查是否为 root 用户
# check_root() {
#     if [[ $EUID -eq 0 ]]; then
#         log_error "请不要使用 root 用户运行此脚本"
#         exit 1
#     fi
# }

# 检查操作系统
check_os() {
    if [[ ! -f /etc/os-release ]]; then
        log_error "不支持的操作系统"
        exit 1
    fi

    . /etc/os-release
    log_info "检测到操作系统: $PRETTY_NAME"
}

# 更新系统包
update_system() {
    log_info "更新系统包..."
    sudo apt update && sudo apt upgrade -y
    log_success "系统包更新完成"
}

# 安装必要依赖
install_dependencies() {
    log_info "安装必要依赖..."
    sudo apt install -y software-properties-common wget curl lib32gcc-s1 lib32stdc++6 libsdl2-2.0-0:i386

    # 添加 i386 架构支持（如果还没有）
    sudo dpkg --add-architecture i386
    sudo apt update
    sudo apt install -y lib32gcc-s1 lib32stdc++6

    log_success "依赖安装完成"
}

# 创建 Steam 用户
create_steam_user() {
    log_info "创建 Steam 用户..."
    if ! id "steam" &>/dev/null; then
        sudo useradd -m -s /bin/bash steam
        log_success "Steam 用户创建完成"
    else
        log_warning "Steam 用户已存在"
    fi
}

# 下载并安装 SteamCMD
install_steamcmd() {
    log_info "下载并安装 SteamCMD..."

    # 切换到 Steam 用户
    sudo -u steam bash << 'EOF'
cd /home/steam

# 下载 SteamCMD
wget https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz

# 创建 SteamCMD 目录
mkdir -p ~/steamcmd
cd ~/steamcmd

# 解压 SteamCMD
tar -xvzf ../steamcmd_linux.tar.gz

# 清理下载文件
rm ../steamcmd_linux.tar.gz

# 测试 SteamCMD
./steamcmd.sh +quit
EOF

    log_success "SteamCMD 安装完成"
}

# 下载 L4D2 服务器
download_l4d2_server() {
    log_info "下载 L4D2 服务器文件..."
    log_warning "这可能需要一些时间，请耐心等待..."

    sudo -u steam bash << 'EOF'
cd /home/steam/steamcmd

# 下载 L4D2 服务器
./steamcmd.sh +force_install_dir /home/steam/l4d2_server +login anonymous +app_update 222860 validate +quit
EOF

    log_success "L4D2 服务器下载完成"
}

# 安装 SourceMod 和 MetaMod
install_sourcemod() {
    log_info "安装 SourceMod 和 MetaMod..."

    sudo -u steam bash << 'EOF'
cd /home/steam

# 下载并安装 MetaMod
wget -O metamod.tar.gz "https://mms.alliedmods.net/mmsdrop/1.11/mmsource-1.11.0-git1148-linux.tar.gz"
tar -xzf metamod.tar.gz -C /home/steam/l4d2_server/left4dead2/
rm metamod.tar.gz

# 下载并安装 SourceMod
wget -O sourcemod.tar.gz "https://sm.alliedmods.net/smdrop/1.11/sourcemod-1.11.0-git6936-linux.tar.gz"
tar -xzf sourcemod.tar.gz -C /home/steam/l4d2_server/left4dead2/
rm sourcemod.tar.gz

# 创建插件目录
mkdir -p /home/steam/l4d2_server/left4dead2/addons/sourcemod/plugins
EOF

    log_success "SourceMod 和 MetaMod 安装完成"
}

# 下载创意工坊内容
download_workshop_content() {
    log_warning "下载创意工坊内容需要有效的Steam账户"
    log_warning "如果下载失败，请使用 /home/download_workshop.sh 脚本手动配置账户"

    sudo -u steam bash << 'EOF'
cd /home/steam/steamcmd

# 尝试使用匿名账户下载（可能失败）
echo "尝试匿名下载..."
./steamcmd.sh +login anonymous +workshop_download_item 550 811732 +workshop_download_item 550 524217 +quit

# 检查是否下载成功
if [[ -d /home/steam/steam/steamapps/workshop/content/550/811732 ]]; then
    cp -r /home/steam/steam/steamapps/workshop/content/550/811732/* /home/steam/l4d2_server/left4dead2/ 2>/dev/null || true
    echo "SourceMod下载成功"
else
    echo "匿名下载失败，请使用专用脚本配置Steam账户"
fi

if [[ -d /home/steam/steam/steamapps/workshop/content/550/524217 ]]; then
    cp -r /home/steam/steam/steamapps/workshop/content/550/524217/* /home/steam/l4d2_server/left4dead2/ 2>/dev/null || true
    echo "MetaMod下载成功"
else
    echo "匿名下载失败，请使用专用脚本配置Steam账户"
fi
EOF

    log_success "创意工坊内容下载完成（可能需要配置Steam账户）"
}

# 配置服务器
configure_server() {
    log_info "配置 L4D2 服务器..."

    # 创建配置文件目录
    sudo -u steam mkdir -p /home/steam/l4d2_server/left4dead2/cfg

    # 创建服务器配置文件
    sudo -u steam cat > /home/steam/l4d2_server/left4dead2/cfg/server.cfg << 'EOF'
hostname "L4D2 Server"
rcon_password "your_rcon_password_here"
sv_password ""  // 设置为空表示无密码
sv_region "255"  // 自动选择区域
sv_lan "0"  // 互联网服务器

// 游戏设置
mp_gamemode "coop"
sv_gametypes "coop"
z_difficulty "Normal"
sv_maxplayers "8"

// 管理员设置 (SteamID64)
admin_steam "STEAM_0:0:12345678"  // 请替换为您的 SteamID64

// 其他设置
sv_allow_lobby_connect_only "0"
sv_consistency "1"
sv_pure "1"
sv_pure_kick_clients "1"
EOF

    # 创建启动脚本
    sudo -u steam cat > /home/steam/l4d2_server/start_server.sh << 'EOF'
#!/bin/bash
cd /home/steam/l4d2_server
./srcds_run -console -game left4dead2 -port 27015 +maxplayers 8 +map c1m1_hotel
EOF

    # 设置启动脚本权限
    sudo -u steam chmod +x /home/steam/l4d2_server/start_server.sh

    # 创建创意工坊配置
    sudo -u steam cat > /home/steam/l4d2_server/left4dead2/cfg/workshop.cfg << 'EOF'
// 创意工坊配置
// 在此处添加您想要的创意工坊物品ID
// 格式: workshop_download_item <appid> <workshop_id>

// 示例：
// workshop_download_item 550 123456789  // 替换为实际的创意工坊ID

// 常用创意工坊ID示例：
// SourceMod: 811732
// MetaMod: 524217
// Admin Menu: 409356
// Basic Chat: 409354

// 添加您的创意工坊物品ID到下方：
// workshop_download_item 550 YOUR_WORKSHOP_ID_HERE
EOF

    log_success "服务器配置完成"
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙..."

    # 检查 ufw 是否安装
    if command -v ufw &> /dev/null; then
        sudo ufw allow 27015/tcp
        sudo ufw allow 27015/udp
        sudo ufw allow 27005/udp  # Steam 端口
        log_success "防火墙配置完成"
    else
        log_warning "未检测到 ufw 防火墙，请手动开放端口 27015 (TCP/UDP) 和 27005 (UDP)"
    fi
}

# 创建服务文件
create_service() {
    log_info "创建系统服务..."

    sudo cat > /etc/systemd/system/l4d2-server.service << 'EOF'
[Unit]
Description=L4D2 Dedicated Server
After=network.target

[Service]
Type=simple
User=steam
WorkingDirectory=/home/steam/l4d2_server
ExecStart=/home/steam/l4d2_server/start_server.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # 重新加载 systemd
    sudo systemctl daemon-reload

    log_success "系统服务创建完成"
}

# 创建管理脚本
create_management_script() {
    log_info "创建服务器管理脚本..."

    cat > /home/steam/manage_server.sh << 'EOF'
#!/bin/bash

# L4D2 服务器管理脚本

case "$1" in
    start)
        sudo systemctl start l4d2-server
        echo "L4D2 服务器已启动"
        ;;
    stop)
        sudo systemctl stop l4d2-server
        echo "L4D2 服务器已停止"
        ;;
    restart)
        sudo systemctl restart l4d2-server
        echo "L4D2 服务器已重启"
        ;;
    status)
        sudo systemctl status l4d2-server
        ;;
    console)
        echo "连接到服务器控制台..."
        echo "使用 Ctrl+C 退出"
        sudo -u steam /home/steam/l4d2_server/srcds_run -console -game left4dead2 -port 27015 +maxplayers 8 +map c1m1_hotel
        ;;
    update)
        echo "更新服务器..."
        sudo -u steam /home/steam/steamcmd/steamcmd.sh +force_install_dir /home/steam/l4d2_server +login anonymous +app_update 222860 validate +quit
        ;;
    workshop)
        echo "下载创意工坊内容..."
        echo "注意：需要有效的Steam账户，请使用 /home/download_workshop.sh 脚本"
        echo "或者确保已配置Steam账户信息"
        echo ""
        echo "请输入创意工坊ID（多个ID用空格分隔）:"
        read -r workshop_ids
        if [[ -n "$workshop_ids" ]]; then
            echo "建议使用专用脚本下载："
            echo "/home/download_workshop.sh $workshop_ids"
            echo ""
            echo "或者使用管理脚本的交互式下载..."
            workshop_cmd=""
            for id in $workshop_ids; do
                workshop_cmd="$workshop_cmd +workshop_download_item 550 $id"
            done
            echo "执行命令：steamcmd.sh +login anonymous $workshop_cmd +quit"
            sudo -u steam /home/steam/steamcmd/steamcmd.sh +login anonymous $workshop_cmd +quit
            echo "创意工坊内容下载完成，请重启服务器以应用更改"
        else
            echo "未输入有效的创意工坊ID"
        fi
        ;;
    mods)
        echo "更新插件..."
        echo "注意：需要有效的Steam账户，请使用 /home/download_workshop.sh 脚本"
        sudo -u steam /home/steam/steamcmd/steamcmd.sh +login anonymous +workshop_download_item 550 811732 +workshop_download_item 550 524217 +quit
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|console|update|workshop|mods}"
        echo "  start     - 启动服务器"
        echo "  stop      - 停止服务器"
        echo "  restart   - 重启服务器"
        echo "  status    - 查看服务器状态"
        echo "  console   - 连接到服务器控制台"
        echo "  update    - 更新服务器文件"
        echo "  workshop  - 下载创意工坊内容"
        echo "  mods      - 更新插件"
        exit 1
        ;;
esac
EOF

    chmod +x /home/steam/manage_server.sh
    log_success "管理脚本创建完成"
}

# 显示使用说明
show_usage() {
    log_success "L4D2 服务器部署完成！"
    echo
    log_info "使用说明:"
    echo "1. 编辑服务器配置: nano /home/steam/l4d2_server/left4dead2/cfg/server.cfg"
    echo "2. 启动服务器: /home/steam/manage_server.sh start"
    echo "3. 查看状态: /home/steam/manage_server.sh status"
    echo "4. 停止服务器: /home/steam/manage_server.sh stop"
    echo "5. 更新服务器: /home/steam/manage_server.sh update"
    echo "6. 下载创意工坊内容: /home/steam/manage_server.sh workshop"
    echo "7. 更新插件: /home/steam/manage_server.sh mods"
    echo
    log_info "服务器信息:"
    echo "- 端口: 27015 (TCP/UDP)"
    echo "- Steam 端口: 27005 (UDP)"
    echo "- 安装目录: /home/steam/l4d2_server"
    echo "- 日志目录: /home/steam/l4d2_server/left4dead2/logs"
    echo
    log_warning "重要提醒:"
    echo "- 请修改 server.cfg 中的 rcon_password"
    echo "- 请将您的 SteamID64 添加到管理员列表"
    echo "- 确保防火墙已正确配置"
    echo "- 首次运行可能需要一些时间来下载内容"
    echo "- 下载创意工坊内容需要有效的Steam账户"
    echo "- 建议使用专门的Steam账户，不要使用主要账户"
}

# 主函数
main() {
    log_info "开始部署 L4D2 服务器..."

    # check_root
    check_os
    update_system
    install_dependencies
    create_steam_user
    install_steamcmd
    download_l4d2_server
    install_sourcemod
    download_workshop_content
    configure_server
    configure_firewall
    create_service
    create_management_script
    show_usage

    log_success "L4D2 服务器部署完成！"
}

# 运行主函数
main "$@"
