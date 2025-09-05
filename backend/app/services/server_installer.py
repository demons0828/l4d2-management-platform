import subprocess
import os
import asyncio
import uuid
from typing import Optional, Dict, Any
from pathlib import Path
from app.core.config import settings
from app.services.download_manager import download_manager


class ServerInstaller:
    """L4D2服务器安装器"""

    def __init__(self):
        self.steamcmd_path = Path(settings.steamcmd_path)
        self.server_path = Path(settings.l4d2_server_path)

    def is_steamcmd_installed(self) -> bool:
        """检查SteamCMD是否已安装"""
        return (self.steamcmd_path / "steamcmd.sh").exists()

    def is_server_installed(self) -> bool:
        """检查L4D2服务器是否已安装"""
        return (self.server_path / "srcds_run").exists()

    def get_installation_status(self) -> Dict[str, Any]:
        """获取安装状态"""
        return {
            "steamcmd_installed": self.is_steamcmd_installed(),
            "server_installed": self.is_server_installed(),
            "steamcmd_path": str(self.steamcmd_path),
            "server_path": str(self.server_path)
        }

    async def install_steamcmd(self) -> Dict[str, Any]:
        """安装SteamCMD"""
        try:
            # 确保目录存在
            self.steamcmd_path.parent.mkdir(parents=True, exist_ok=True)

            # 下载SteamCMD
            download_cmd = [
                "wget",
                "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz",
                "-O", "/tmp/steamcmd.tar.gz"
            ]

            result = await asyncio.get_event_loop().run_in_executor(
                None, lambda: subprocess.run(download_cmd, capture_output=True, text=True)
            )

            if result.returncode != 0:
                return {
                    "success": False,
                    "message": f"下载SteamCMD失败: {result.stderr}"
                }

            # 解压SteamCMD
            extract_cmd = ["tar", "-xzf", "/tmp/steamcmd.tar.gz", "-C", str(self.steamcmd_path.parent)]

            result = await asyncio.get_event_loop().run_in_executor(
                None, lambda: subprocess.run(extract_cmd, capture_output=True, text=True)
            )

            if result.returncode != 0:
                return {
                    "success": False,
                    "message": f"解压SteamCMD失败: {result.stderr}"
                }

            # 清理下载文件
            os.remove("/tmp/steamcmd.tar.gz")

            return {
                "success": True,
                "message": "SteamCMD安装成功"
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"安装SteamCMD失败: {str(e)}"
            }

    async def download_l4d2_server(self, steam_credentials: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """下载L4D2服务器"""
        try:
            if not self.is_steamcmd_installed():
                return {
                    "success": False,
                    "message": "SteamCMD未安装，请先安装SteamCMD"
                }

            # 确保服务器目录存在
            self.server_path.mkdir(parents=True, exist_ok=True)

            # 构建SteamCMD命令
            cmd = [
                str(self.steamcmd_path / "steamcmd.sh"),
                "+force_install_dir", str(self.server_path)
            ]

            # 添加认证信息
            if steam_credentials and steam_credentials.get("username"):
                cmd.extend([
                    "+login", steam_credentials["username"],
                    steam_credentials.get("password", "")
                ])
            else:
                cmd.extend(["+login", "anonymous"])

            # 添加下载命令
            cmd.extend([
                "+app_update", "222860", "validate",
                "+quit"
            ])

            # 创建下载任务
            task_id = f"l4d2_server_{uuid.uuid4().hex[:8]}"
            task = download_manager.create_task(
                task_id=task_id,
                task_type="l4d2_server",
                description="下载L4D2服务器"
            )

            # 启动下载进程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.steamcmd_path.parent)
            )

            # 启动进度监控
            asyncio.create_task(
                download_manager.monitor_download_progress(task_id, process, self.server_path)
            )

            return {
                "success": True,
                "message": "L4D2服务器下载已开始",
                "task_id": task_id
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "下载超时，请检查网络连接"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"下载L4D2服务器失败: {str(e)}"
            }

    async def install_sourcemod_and_metamod(self, steam_credentials: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """安装SourceMod和MetaMod"""
        try:
            if not self.is_server_installed():
                return {
                    "success": False,
                    "message": "L4D2服务器未安装，请先安装服务器"
                }

            # 安装MetaMod
            metamod_cmd = [
                str(self.steamcmd_path / "steamcmd.sh")
            ]

            if steam_credentials and steam_credentials.get("username"):
                metamod_cmd.extend([
                    "+login", steam_credentials["username"],
                    steam_credentials.get("password", "")
                ])
            else:
                metamod_cmd.extend(["+login", "anonymous"])

            metamod_cmd.extend([
                "+workshop_download_item", "550", "524217",
                "+quit"
            ])

            result = await asyncio.get_event_loop().run_in_executor(
                None, lambda: subprocess.run(metamod_cmd, capture_output=True, text=True)
            )

            if result.returncode != 0:
                return {
                    "success": False,
                    "message": f"下载MetaMod失败: {result.stderr}"
                }

            # 安装SourceMod
            sourcemod_cmd = [
                str(self.steamcmd_path / "steamcmd.sh")
            ]

            if steam_credentials and steam_credentials.get("username"):
                sourcemod_cmd.extend([
                    "+login", steam_credentials["username"],
                    steam_credentials.get("password", "")
                ])
            else:
                sourcemod_cmd.extend(["+login", "anonymous"])

            sourcemod_cmd.extend([
                "+workshop_download_item", "550", "811732",
                "+quit"
            ])

            result = await asyncio.get_event_loop().run_in_executor(
                None, lambda: subprocess.run(sourcemod_cmd, capture_output=True, text=True)
            )

            if result.returncode != 0:
                return {
                    "success": False,
                    "message": f"下载SourceMod失败: {result.stderr}"
                }

            # 复制文件到服务器目录
            workshop_path = self.server_path / "steam" / "steamapps" / "workshop" / "content" / "550"

            # 复制MetaMod
            metamod_source = workshop_path / "524217"
            if metamod_source.exists():
                result = await asyncio.get_event_loop().run_in_executor(
                    None, subprocess.run,
                    ["cp", "-r", str(metamod_source / "*"), str(self.server_path / "left4dead2")],
                    {"capture_output": True, "text": True}
                )

            # 复制SourceMod
            sourcemod_source = workshop_path / "811732"
            if sourcemod_source.exists():
                result = await asyncio.get_event_loop().run_in_executor(
                    None, subprocess.run,
                    ["cp", "-r", str(sourcemod_source / "*"), str(self.server_path / "left4dead2")],
                    {"capture_output": True, "text": True}
                )

            return {
                "success": True,
                "message": "SourceMod和MetaMod安装完成"
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"安装插件失败: {str(e)}"
            }

    async def full_installation(self, steam_credentials: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """完整安装流程"""
        results = []

        # 1. 安装SteamCMD（如果还没有）
        if not self.is_steamcmd_installed():
            steamcmd_result = await self.install_steamcmd()
            results.append({"step": "steamcmd", **steamcmd_result})
            if not steamcmd_result["success"]:
                return {
                    "success": False,
                    "message": "SteamCMD安装失败",
                    "results": results
                }

        # 2. 下载L4D2服务器
        server_result = await self.download_l4d2_server(steam_credentials)
        results.append({"step": "server", **server_result})
        if not server_result["success"]:
            return {
                "success": False,
                "message": "服务器下载失败",
                "results": results
            }

        # 3. 安装插件
        plugins_result = await self.install_sourcemod_and_metamod(steam_credentials)
        results.append({"step": "plugins", **plugins_result})

        # 检查整体安装结果
        all_success = all(result["success"] for result in results)

        return {
            "success": all_success,
            "message": "安装完成" if all_success else "安装过程中出现错误",
            "results": results
        }
