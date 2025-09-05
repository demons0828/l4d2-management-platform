from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class RoomBase(BaseModel):
    name: str
    server_id: int
    max_players: Optional[int] = 8
    is_private: Optional[bool] = False
    password: Optional[str] = None
    game_mode: Optional[str] = "coop"
    current_map: Optional[str] = "c1m1_hotel"


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    name: Optional[str] = None
    max_players: Optional[int] = None
    is_private: Optional[bool] = None
    password: Optional[str] = None
    game_mode: Optional[str] = None
    current_map: Optional[str] = None
    is_active: Optional[bool] = None


class Room(RoomBase):
    id: int
    creator_id: int
    current_players: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class RoomPlayerBase(BaseModel):
    room_id: int
    user_id: int


class RoomPlayer(RoomPlayerBase):
    id: int
    joined_at: datetime

    class Config:
        from_attributes = True


class RoomJoinRequest(BaseModel):
    room_id: int
    password: Optional[str] = None


class RoomJoinResponse(BaseModel):
    success: bool
    message: str
    room: Optional[Room] = None
