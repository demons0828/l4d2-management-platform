from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user, create_access_token, verify_password, get_password_hash
from app.services.steam_auth import SteamAuthService
from app.models.user import User
from app.schemas.user import (
    User as UserSchema,
    SteamAuthResponse,
    LoginRequest,
    RegisterRequest,
    AuthResponse
)

router = APIRouter()


@router.post("/steam/login", response_model=SteamAuthResponse)
async def steam_login(steam_id: str, db: Session = Depends(get_db)):
    """Steam登录"""
    auth_result = await SteamAuthService.authenticate_user(steam_id)

    if not auth_result["success"]:
        raise HTTPException(status_code=400, detail=auth_result["message"])

    # 检查用户是否已存在
    user = db.query(User).filter(User.steam_id == steam_id).first()

    if not user:
        # 创建新用户
        user = User(
            steam_id=steam_id,
            username=auth_result["username"],
            avatar_url=auth_result.get("avatar_url")
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return SteamAuthResponse(**auth_result)


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """账号密码登录"""
    user = db.query(User).filter(User.email == request.email).first()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=400, detail="邮箱或密码错误")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="账号已被禁用")

    # 生成访问token
    access_token = create_access_token(data={"sub": str(user.id)})

    return AuthResponse(
        success=True,
        user=user,
        token=access_token,
        message="登录成功"
    )


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查邮箱是否已存在
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    # 创建新用户
    hashed_password = get_password_hash(request.password)
    user = User(
        username=request.username,
        email=request.email,
        password_hash=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # 生成访问token
    access_token = create_access_token(data={"sub": str(user.id)})

    return AuthResponse(
        success=True,
        user=user,
        token=access_token,
        message="注册成功"
    )


@router.post("/logout")
async def logout():
    """登出（客户端处理token清除）"""
    return {"message": "已登出"}
