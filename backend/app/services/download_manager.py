import asyncio
import time
import threading
from typing import Dict, Any, Optional
from pathlib import Path
import subprocess
import psutil
import os


class DownloadTask:
    """下载任务类"""

    def __init__(self, task_id: str, task_type: str, description: str):
        self.task_id = task_id
        self.task_type = task_type
        self.description = description
        self.status = "pending"  # pending, running, completed, failed
        self.progress = 0
        self.message = ""
        self.start_time = None
        self.end_time = None
        self.process = None
        self.total_size = 0
        self.downloaded_size = 0

    def start(self):
        self.status = "running"
        self.start_time = time.time()

    def complete(self, message: str = "完成"):
        self.status = "completed"
        self.progress = 100
        self.message = message
        self.end_time = time.time()

    def fail(self, message: str):
        self.status = "failed"
        self.message = message
        self.end_time = time.time()

    def update_progress(self, progress: int, message: str = ""):
        self.progress = max(0, min(100, progress))
        if message:
            self.message = message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "description": self.description,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": (self.end_time - self.start_time) if self.start_time and self.end_time else None,
            "total_size": self.total_size,
            "downloaded_size": self.downloaded_size
        }


class DownloadManager:
    """下载管理器"""

    def __init__(self):
        self.tasks: Dict[str, DownloadTask] = {}
        self._lock = threading.Lock()

    def create_task(self, task_id: str, task_type: str, description: str) -> DownloadTask:
        """创建下载任务"""
        with self._lock:
            task = DownloadTask(task_id, task_type, description)
            self.tasks[task_id] = task
            return task

    def get_task(self, task_id: str) -> Optional[DownloadTask]:
        """获取下载任务"""
        with self._lock:
            return self.tasks.get(task_id)

    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """获取所有任务"""
        with self._lock:
            return {task_id: task.to_dict() for task_id, task in self.tasks.items()}

    def update_task_progress(self, task_id: str, progress: int, message: str = ""):
        """更新任务进度"""
        with self._lock:
            task = self.tasks.get(task_id)
            if task:
                task.update_progress(progress, message)

    def complete_task(self, task_id: str, message: str = "完成"):
        """完成任务"""
        with self._lock:
            task = self.tasks.get(task_id)
            if task:
                task.complete(message)

    def fail_task(self, task_id: str, message: str):
        """任务失败"""
        with self._lock:
            task = self.tasks.get(task_id)
            if task:
                task.fail(message)

    async def monitor_download_progress(self, task_id: str, process: subprocess.Popen, server_path: Path):
        """监控下载进度"""
        task = self.get_task(task_id)
        if not task:
            return

        task.start()

        try:
            # 监控目录大小变化
            initial_size = self._get_directory_size(server_path)

            while process.poll() is None:
                await asyncio.sleep(2)  # 每2秒更新一次

                current_size = self._get_directory_size(server_path)
                size_diff = current_size - initial_size

                # 估算进度（L4D2服务器大约需要8-10GB）
                estimated_total = 10 * 1024 * 1024 * 1024  # 10GB
                progress = min(95, int((size_diff / estimated_total) * 100))

                task.update_progress(progress, f"已下载: {size_diff / (1024*1024*1024):.1f} GB")

            # 等待进程完成
            return_code = process.wait()

            if return_code == 0:
                final_size = self._get_directory_size(server_path)
                downloaded = final_size - initial_size
                task.complete(f"下载完成，共下载 {downloaded / (1024*1024*1024):.1f} GB")
            else:
                task.fail("下载失败")

        except Exception as e:
            task.fail(f"监控出错: {str(e)}")

    def _get_directory_size(self, path: Path) -> int:
        """获取目录大小"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except OSError:
                        pass
        except Exception:
            pass
        return total_size


# 全局下载管理器实例
download_manager = DownloadManager()
