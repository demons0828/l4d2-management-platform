from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ServerStatus(str, enum.Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class GameMode(str, enum.Enum):
    COOP = "coop"
    VERSUS = "versus"
    SURVIVAL = "survival"
    SCAVENGE = "scavenge"


class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    host = Column(String, default="localhost")
    port = Column(Integer, default=27015)
    max_players = Column(Integer, default=8)
    status = Column(Enum(ServerStatus), default=ServerStatus.STOPPED)
    current_map = Column(String, default="c1m1_hotel")
    game_mode = Column(Enum(GameMode), default=GameMode.COOP)
    difficulty = Column(String, default="Normal")
    password = Column(String, nullable=True)
    rcon_password = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
