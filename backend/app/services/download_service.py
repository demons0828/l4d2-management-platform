import asyncio
import subprocess
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from app.core.config import settings


class DownloadService:
    """多线程下载服务"""

    def __init__(self):
        self.steamcmd_path = Path(settings.steamcmd_path)
        self.workshop_content_path = Path(settings.l4d2_server_path) / "steam" / "steamapps" / "workshop" / "content" / "550"
        self.executor = ThreadPoolExecutor(max_workers=settings.download_workers)

    async def download_workshop_items(self, workshop_ids: List[str]) -> Dict[str, Any]:
        """下载创意工坊物品"""
        if not self.steamcmd_path.exists():
            return {
                "success": False,
                "message": "SteamCMD未找到，请先安装SteamCMD"
            }

        # 检查Steam配置
        steam_config = self._load_steam_config()
        if not steam_config:
            return {
                "success": False,
                "message": "未找到Steam账户配置，请先配置Steam账户"
            }

        tasks = []
        for workshop_id in workshop_ids:
            task = asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._download_single_item,
                workshop_id,
                steam_config
            )
            tasks.append(task)

        # 并发执行下载任务
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        successful = []
        failed = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed.append({
                    "workshop_id": workshop_ids[i],
                    "error": str(result)
                })
            elif result["success"]:
                successful.append(result)
            else:
                failed.append(result)

        return {
            "success": len(successful) > 0,
            "message": f"下载完成：{len(successful)}成功，{len(failed)}失败",
            "successful": successful,
            "failed": failed
        }

    def _download_single_item(self, workshop_id: str, steam_config: Dict[str, str]) -> Dict[str, Any]:
        """下载单个创意工坊物品"""
        try:
            cmd = [
                str(self.steamcmd_path / "steamcmd.sh"),
                "+login", steam_config["username"], steam_config.get("password", ""),
                "+workshop_download_item", "550", workshop_id,
                "+quit"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )

            if result.returncode == 0:
                # 复制文件到服务器目录
                self._copy_to_server_directory(workshop_id)

                return {
                    "success": True,
                    "workshop_id": workshop_id,
                    "message": "下载成功"
                }
            else:
                return {
                    "success": False,
                    "workshop_id": workshop_id,
                    "error": result.stderr.strip()
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "workshop_id": workshop_id,
                "error": "下载超时"
            }
        except Exception as e:
            return {
                "success": False,
                "workshop_id": workshop_id,
                "error": str(e)
            }

    def _load_steam_config(self) -> Optional[Dict[str, str]]:
        """加载Steam配置"""
        config_path = Path(settings.steam_config_path)
        if not config_path.exists():
            return None

        config = {}
        try:
            with open(config_path, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        config[key] = value.strip('"')
        except Exception:
            return None

        return config

    def _copy_to_server_directory(self, workshop_id: str):
        """将下载的文件复制到服务器目录"""
        workshop_dir = self.workshop_content_path / workshop_id
        server_dir = Path(settings.l4d2_server_path) / "left4dead2"

        if workshop_dir.exists() and server_dir.exists():
            import shutil
            try:
                # 复制所有文件
                for item in workshop_dir.iterdir():
                    if item.is_file():
                        shutil.copy2(item, server_dir)
                    elif item.is_dir():
                        dest_dir = server_dir / item.name
                        if dest_dir.exists():
                            shutil.rmtree(dest_dir)
                        shutil.copytree(item, dest_dir)
            except Exception as e:
                print(f"复制文件失败: {e}")

    async def get_download_progress(self, workshop_ids: List[str]) -> Dict[str, Any]:
        """获取下载进度"""
        # 这里可以实现更复杂的进度跟踪
        # 目前简化处理
        progress = {}
        for workshop_id in workshop_ids:
            workshop_dir = self.workshop_content_path / workshop_id
            if workshop_dir.exists():
                progress[workshop_id] = 100
            else:
                progress[workshop_id] = 0

        return {
            "progress": progress,
            "completed": sum(1 for p in progress.values() if p == 100),
            "total": len(workshop_ids)
        }
