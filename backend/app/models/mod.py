from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class WorkshopItem(Base):
    __tablename__ = "workshop_items"

    id = Column(Integer, primary_key=True, index=True)
    workshop_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    author = Column(String, nullable=True)
    preview_url = Column(String, nullable=True)
    file_size = Column(String, nullable=True)
    item_type = Column(String, nullable=False)  # mod, map, etc.
    is_installed = Column(Boolean, default=False)
    install_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关联下载任务
    download_tasks = relationship("DownloadTask", back_populates="workshop_item")


class DownloadTask(Base):
    __tablename__ = "download_tasks"

    id = Column(Integer, primary_key=True, index=True)
    workshop_item_id = Column(Integer, ForeignKey("workshop_items.id"))
    status = Column(String, default="pending")  # pending, downloading, completed, failed
    progress = Column(Integer, default=0)  # 0-100
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关联工作坊物品
    workshop_item = relationship("WorkshopItem", back_populates="download_tasks")
