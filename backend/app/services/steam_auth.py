import httpx
import subprocess
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
from app.core.config import settings


class SteamAuthService:
    """Steam认证服务"""

    STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
    STEAM_API_URL = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"

    @staticmethod
    async def get_steam_user_info(steam_id: str) -> Optional[Dict[str, Any]]:
        """获取Steam用户信息"""
        if not settings.steam_api_key:
            return None

        params = {
            "key": settings.steam_api_key,
            "steamids": steam_id
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(SteamAuthService.STEAM_API_URL, params=params)
                response.raise_for_status()
                data = response.json()

                if "response" in data and "players" in data["response"]:
                    players = data["response"]["players"]
                    if players:
                        return players[0]

            except Exception as e:
                print(f"Error fetching Steam user info: {e}")
                return None

        return None

    @staticmethod
    def validate_steam_id(steam_id: str) -> bool:
        """验证Steam ID格式"""
        # Steam ID通常是17位数字
        return steam_id.isdigit() and len(steam_id) == 17

    @staticmethod
    def steam_id_to_steam64(steam_id: str) -> Optional[str]:
        """将Steam ID转换为Steam64 ID"""
        # 这里简化处理，实际项目中可能需要更复杂的转换
        if SteamAuthService.validate_steam_id(steam_id):
            return steam_id
        return None

    @staticmethod
    async def authenticate_user(steam_id: str) -> Dict[str, Any]:
        """认证用户并获取信息"""
        if not SteamAuthService.validate_steam_id(steam_id):
            return {
                "success": False,
                "message": "无效的Steam ID"
            }

        user_info = await SteamAuthService.get_steam_user_info(steam_id)

        if user_info:
            return {
                "success": True,
                "steam_id": steam_id,
                "username": user_info.get("personaname", "Unknown"),
                "avatar_url": user_info.get("avatarfull"),
                "message": "认证成功"
            }
        else:
            return {
                "success": True,
                "steam_id": steam_id,
                "username": f"Steam User {steam_id}",
                "avatar_url": None,
                "message": "认证成功，但无法获取详细信息"
            }

    @staticmethod
    async def validate_steamcmd_credentials(username: str, password: str) -> Dict[str, Any]:
        """验证SteamCMD登录凭据"""
        try:
            steamcmd_path = Path(settings.steamcmd_path) / "steamcmd.sh"

            if not steamcmd_path.exists():
                return {
                    "success": False,
                    "message": "SteamCMD未找到，请先安装SteamCMD"
                }

            # 使用SteamCMD验证登录
            cmd = [
                str(steamcmd_path),
                "+login", username, password,
                "+quit"
            ]

            result = await asyncio.get_event_loop().run_in_executor(
                None, lambda: subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
            )

            if result.returncode == 0 and "FAILED login" not in result.stderr:
                return {
                    "success": True,
                    "message": "SteamCMD登录验证成功"
                }
            else:
                return {
                    "success": False,
                    "message": "SteamCMD登录失败，请检查用户名和密码"
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "验证超时，请重试"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"验证失败: {str(e)}"
            }
