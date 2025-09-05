from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.download_service import DownloadService
from app.models.mod import WorkshopItem, DownloadTask
from app.schemas.mod import (
    WorkshopItem as WorkshopItemSchema,
    WorkshopDownloadRequest,
    WorkshopDownloadResponse,
    DownloadTask as DownloadTaskSchema
)

router = APIRouter()
download_service = DownloadService()


@router.get("/workshop", response_model=List[WorkshopItemSchema])
async def get_workshop_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取创意工坊物品列表"""
    items = db.query(WorkshopItem).offset(skip).limit(limit).all()
    return items


@router.post("/workshop/download", response_model=WorkshopDownloadResponse)
async def download_workshop_items(
    request: WorkshopDownloadRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """下载创意工坊物品"""
    # 创建下载任务记录
    tasks = []
    for workshop_id in request.workshop_ids:
        # 检查是否已存在
        existing_item = db.query(WorkshopItem).filter(
            WorkshopItem.workshop_id == workshop_id
        ).first()

        if not existing_item:
            # 创建新的工作坊物品记录
            item = WorkshopItem(
                workshop_id=workshop_id,
                title=f"Workshop Item {workshop_id}",
                item_type="unknown"
            )
            db.add(item)
            db.commit()
            db.refresh(item)
        else:
            item = existing_item

        # 创建下载任务
        task = DownloadTask(
            workshop_item_id=item.id,
            status="pending"
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        tasks.append(task)

    # 后台执行下载
    background_tasks.add_task(
        download_service.download_workshop_items,
        request.workshop_ids
    )

    return WorkshopDownloadResponse(
        success=True,
        message=f"已开始下载 {len(request.workshop_ids)} 个物品",
        tasks=tasks
    )


@router.get("/workshop/{workshop_id}", response_model=WorkshopItemSchema)
async def get_workshop_item(workshop_id: str, db: Session = Depends(get_db)):
    """获取创意工坊物品详情"""
    item = db.query(WorkshopItem).filter(WorkshopItem.workshop_id == workshop_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="物品未找到")
    return item


@router.get("/downloads", response_model=List[DownloadTaskSchema])
async def get_download_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取下载任务列表"""
    tasks = db.query(DownloadTask).offset(skip).limit(limit).all()
    return tasks


@router.get("/downloads/{task_id}", response_model=DownloadTaskSchema)
async def get_download_task(task_id: int, db: Session = Depends(get_db)):
    """获取下载任务详情"""
    task = db.query(DownloadTask).filter(DownloadTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务未找到")
    return task


@router.delete("/workshop/{workshop_id}")
async def uninstall_workshop_item(
    workshop_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """卸载创意工坊物品"""
    item = db.query(WorkshopItem).filter(WorkshopItem.workshop_id == workshop_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="物品未找到")

    # 这里可以添加实际的卸载逻辑
    item.is_installed = False
    db.commit()

    return {"message": "物品已卸载"}
