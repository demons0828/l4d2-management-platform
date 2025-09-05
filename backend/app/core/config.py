from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 应用配置
    app_name: str = "L4D2 Management Platform"
    app_version: str = "1.0.0"
    debug: bool = True

    # 数据库配置
    database_url: str = "sqlite:///./l4d2_manager.db"

    # JWT配置
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Steam API配置
    steam_api_key: Optional[str] = None

    # 服务器配置
    l4d2_server_path: str = "/home/steam/l4d2_server"
    steamcmd_path: str = "/home/steam/steamcmd"
    steam_config_path: str = "/home/steam/.steam_config"

    # 工作配置
    download_workers: int = 4
    max_download_concurrent: int = 3

    # Redis配置（可选，用于缓存）
    redis_url: Optional[str] = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
