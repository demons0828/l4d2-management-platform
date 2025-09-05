from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class WorkshopItemBase(BaseModel):
    workshop_id: str
    title: str
    description: Optional[str] = None
    author: Optional[str] = None
    preview_url: Optional[str] = None
    file_size: Optional[str] = None
    item_type: str


class WorkshopItemCreate(WorkshopItemBase):
    pass


class WorkshopItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    preview_url: Optional[str] = None
    file_size: Optional[str] = None
    item_type: Optional[str] = None
    is_installed: Optional[bool] = None
    install_path: Optional[str] = None


class WorkshopItem(WorkshopItemBase):
    id: int
    is_installed: bool
    install_path: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class DownloadTaskBase(BaseModel):
    workshop_item_id: int


class DownloadTaskCreate(DownloadTaskBase):
    pass


class DownloadTask(DownloadTaskBase):
    id: int
    status: str
    progress: int
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]
    workshop_item: WorkshopItem

    class Config:
        from_attributes = True


class WorkshopSearchQuery(BaseModel):
    query: str
    item_type: Optional[str] = None
    limit: Optional[int] = 20
    offset: Optional[int] = 0


class WorkshopDownloadRequest(BaseModel):
    workshop_ids: List[str]


class WorkshopDownloadResponse(BaseModel):
    success: bool
    message: str
    tasks: List[DownloadTask]
