import subprocess
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.auth import get_current_admin_user
from app.services.server_manager import ServerManager
from app.services.server_installer import ServerInstaller
from app.services.steam_auth import SteamAuthService
from app.services.download_manager import download_manager
from app.models.server import Server
from app.schemas.server import (
    Server as ServerSchema,
    ServerCreate,
    ServerUpdate,
    ServerControl,
    ServerStatusResponse
)

router = APIRouter()
server_manager = ServerManager()


# 安装相关路由（必须放在前面，避免与{server_id}冲突）
@router.get("/install/status")
async def get_installation_status():
    """获取服务器安装状态"""
    installer = ServerInstaller()
    return installer.get_installation_status()


@router.post("/install/steamcmd")
async def install_steamcmd(current_user = Depends(get_current_admin_user)):
    """安装SteamCMD"""
    installer = ServerInstaller()
    return await installer.install_steamcmd()


@router.post("/install/server")
async def install_l4d2_server(
    steam_username: str = None,
    steam_password: str = None,
    current_user = Depends(get_current_admin_user)
):
    """安装L4D2服务器"""
    # 验证SteamCMD凭据（如果提供）
    if steam_username and steam_password:
        validation_result = await SteamAuthService.validate_steamcmd_credentials(steam_username, steam_password)
        if not validation_result["success"]:
            raise HTTPException(status_code=400, detail=validation_result["message"])

    installer = ServerInstaller()
    credentials = None
    if steam_username and steam_password:
        credentials = {"username": steam_username, "password": steam_password}

    return await installer.download_l4d2_server(credentials)


@router.post("/install/plugins")
async def install_plugins(
    steam_username: str = None,
    steam_password: str = None,
    current_user = Depends(get_current_admin_user)
):
    """安装SourceMod和MetaMod"""
    installer = ServerInstaller()
    credentials = None
    if steam_username and steam_password:
        credentials = {"username": steam_username, "password": steam_password}

    return await installer.install_sourcemod_and_metamod(credentials)


@router.post("/install/full")
async def full_installation(
    steam_username: str = None,
    steam_password: str = None,
    current_user = Depends(get_current_admin_user)
):
    """完整安装（SteamCMD + L4D2服务器 + 插件）"""
    # 验证SteamCMD凭据（如果提供）
    if steam_username and steam_password:
        validation_result = await SteamAuthService.validate_steamcmd_credentials(steam_username, steam_password)
        if not validation_result["success"]:
            raise HTTPException(status_code=400, detail=validation_result["message"])

    installer = ServerInstaller()
    credentials = None
    if steam_username and steam_password:
        credentials = {"username": steam_username, "password": steam_password}

    return await installer.full_installation(credentials)


# 下载任务管理端点
@router.get("/downloads")
async def get_download_tasks():
    """获取所有下载任务"""
    return download_manager.get_all_tasks()


@router.get("/downloads/{task_id}")
async def get_download_task(task_id: str):
    """获取下载任务详情"""
    task = download_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="下载任务不存在")
    return task.to_dict()


@router.delete("/downloads/{task_id}")
async def cancel_download_task(task_id: str, current_user = Depends(get_current_admin_user)):
    """取消下载任务"""
    task = download_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="下载任务不存在")

    if task.status == "running" and task.process:
        try:
            task.process.terminate()
            task.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            task.process.kill()

    download_manager.fail_task(task_id, "任务已被取消")
    return {"message": "下载任务已取消"}


@router.get("/", response_model=List[ServerSchema])
async def get_servers(db: Session = Depends(get_db)):
    """获取所有服务器"""
    servers = db.query(Server).all()
    return servers


@router.post("/", response_model=ServerSchema)
async def create_server(
    server: ServerCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """创建新服务器"""
    db_server = Server(**server.dict())
    db.add(db_server)
    db.commit()
    db.refresh(db_server)
    return db_server


@router.get("/{server_id}", response_model=ServerSchema)
async def get_server(server_id: int, db: Session = Depends(get_db)):
    """获取服务器详情"""
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="服务器未找到")
    return server


@router.put("/{server_id}", response_model=ServerSchema)
async def update_server(
    server_id: int,
    server_update: ServerUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """更新服务器"""
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="服务器未找到")

    for field, value in server_update.dict(exclude_unset=True).items():
        setattr(server, field, value)

    db.commit()
    db.refresh(server)
    return server


@router.post("/{server_id}/control", response_model=ServerStatusResponse)
async def control_server(
    server_id: int,
    control: ServerControl,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """控制服务器（启动/停止/重启）"""
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="服务器未找到")

    action = control.action.lower()

    if action == "start":
        result = server_manager.start_server(server.__dict__)
        if result["success"]:
            server.status = "running"
    elif action == "stop":
        result = server_manager.stop_server()
        if result["success"]:
            server.status = "stopped"
    elif action == "restart":
        result = server_manager.restart_server(server.__dict__)
        if result["success"]:
            server.status = "running"
    else:
        raise HTTPException(status_code=400, detail="无效的操作")

    db.commit()

    return ServerStatusResponse(
        success=result["success"],
        status=server.status,
        message=result["message"]
    )


@router.post("/{server_id}/update", response_model=ServerStatusResponse)
async def update_server_files(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """更新服务器文件"""
    result = server_manager.update_server()
    return ServerStatusResponse(
        success=result["success"],
        status="running" if result["success"] else "error",
        message=result["message"]
    )


@router.get("/{server_id}/status")
async def get_server_status(server_id: int):
    """获取服务器状态"""
    status_info = server_manager.get_server_info()
    return {
        "server_id": server_id,
        "status": status_info
    }


