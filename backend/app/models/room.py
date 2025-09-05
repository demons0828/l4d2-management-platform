from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    server_id = Column(Integer, ForeignKey("servers.id"))
    creator_id = Column(Integer, ForeignKey("users.id"))
    current_players = Column(Integer, default=0)
    max_players = Column(Integer, default=8)
    is_private = Column(Boolean, default=False)
    password = Column(String, nullable=True)
    game_mode = Column(String, default="coop")
    current_map = Column(String, default="c1m1_hotel")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关联服务器和创建者
    server = relationship("Server", backref="rooms")
    creator = relationship("User", backref="created_rooms")

    # 关联房间玩家
    players = relationship("RoomPlayer", back_populates="room")


class RoomPlayer(Base):
    __tablename__ = "room_players"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联房间和用户
    room = relationship("Room", back_populates="players")
    user = relationship("User", backref="room_participations")
