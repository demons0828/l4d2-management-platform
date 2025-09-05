from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.server import ServerStatus, GameMode


class ServerBase(BaseModel):
    name: str
    host: Optional[str] = "localhost"
    port: Optional[int] = 27015
    max_players: Optional[int] = 8
    current_map: Optional[str] = "c1m1_hotel"
    game_mode: Optional[GameMode] = GameMode.COOP
    difficulty: Optional[str] = "Normal"
    password: Optional[str] = None
    rcon_password: Optional[str] = None


class ServerCreate(ServerBase):
    pass


class ServerUpdate(BaseModel):
    name: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    max_players: Optional[int] = None
    current_map: Optional[str] = None
    game_mode: Optional[GameMode] = None
    difficulty: Optional[str] = None
    password: Optional[str] = None
    rcon_password: Optional[str] = None


class Server(ServerBase):
    id: int
    status: ServerStatus
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ServerControl(BaseModel):
    action: str  # start, stop, restart


class ServerStatusResponse(BaseModel):
    success: bool
    status: ServerStatus
    message: Optional[str] = None
    details: Optional[dict] = None
