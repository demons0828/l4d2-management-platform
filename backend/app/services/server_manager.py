import subprocess
import os
import signal
from typing import Optional, Dict, Any
from pathlib import Path
from app.core.config import settings
from app.models.server import ServerStatus


class ServerManager:
    """L4D2服务器管理器"""

    def __init__(self):
        self.server_path = Path(settings.l4d2_server_path)
        self.steamcmd_path = Path(settings.steamcmd_path)
        self.process = None

    def is_server_running(self) -> bool:
        """检查服务器是否正在运行"""
        if self.process is None:
            return False
        return self.process.poll() is None

    def get_server_status(self) -> Dict[str, Any]:
        """获取服务器状态"""
        running = self.is_server_running()
        return {
            "running": running,
            "status": ServerStatus.RUNNING if running else ServerStatus.STOPPED,
            "pid": self.process.pid if self.process else None
        }

    def start_server(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """启动服务器"""
        try:
            if self.is_server_running():
                return {
                    "success": False,
                    "message": "服务器已经在运行"
                }

            # 构建启动命令
            cmd = [
                str(self.server_path / "srcds_run"),
                "-console",
                "-game", "left4dead2",
                "-port", str(config.get("port", 27015)),
                "+maxplayers", str(config.get("max_players", 8)),
                "+map", config.get("current_map", "c1m1_hotel"),
                "+sv_gametypes", config.get("game_mode", "coop"),
                "+z_difficulty", config.get("difficulty", "Normal")
            ]

            # 如果设置了密码
            if config.get("password"):
                cmd.extend(["+sv_password", config["password"]])

            # 如果设置了RCON密码
            if config.get("rcon_password"):
                cmd.extend(["+rcon_password", config["rcon_password"]])

            # 启动进程
            self.process = subprocess.Popen(
                cmd,
                cwd=str(self.server_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            return {
                "success": True,
                "message": "服务器启动中...",
                "pid": self.process.pid
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"启动服务器失败: {str(e)}"
            }

    def stop_server(self) -> Dict[str, Any]:
        """停止服务器"""
        try:
            if not self.is_server_running():
                return {
                    "success": False,
                    "message": "服务器未在运行"
                }

            # 发送终止信号
            self.process.terminate()

            # 等待进程结束
            try:
                self.process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                # 如果进程没有在30秒内结束，强制杀死
                self.process.kill()
                self.process.wait()

            self.process = None

            return {
                "success": True,
                "message": "服务器已停止"
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"停止服务器失败: {str(e)}"
            }

    def restart_server(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """重启服务器"""
        stop_result = self.stop_server()
        if not stop_result["success"]:
            return stop_result

        # 等待一会儿再启动
        import time
        time.sleep(2)

        return self.start_server(config)

    def update_server(self) -> Dict[str, Any]:
        """更新服务器"""
        try:
            cmd = [
                str(self.steamcmd_path / "steamcmd.sh"),
                "+force_install_dir", str(self.server_path),
                "+login", "anonymous",
                "+app_update", "222860", "validate",
                "+quit"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "服务器更新完成"
                }
            else:
                return {
                    "success": False,
                    "message": f"服务器更新失败: {result.stderr}"
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"更新服务器失败: {str(e)}"
            }

    def get_server_info(self) -> Dict[str, Any]:
        """获取服务器信息"""
        info = self.get_server_status()
        info.update({
            "server_path": str(self.server_path),
            "steamcmd_path": str(self.steamcmd_path),
            "config_exists": (self.server_path / "left4dead2" / "cfg" / "server.cfg").exists()
        })
        return info
