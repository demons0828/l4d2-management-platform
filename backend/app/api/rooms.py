from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.room import Room, RoomPlayer
from app.models.user import User
from app.schemas.room import (
    Room as RoomSchema,
    RoomCreate,
    RoomUpdate,
    RoomJoinRequest,
    RoomJoinResponse,
    RoomPlayer as RoomPlayerSchema
)

router = APIRouter()


@router.get("/", response_model=List[RoomSchema])
async def get_rooms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取房间列表"""
    rooms = db.query(Room).filter(Room.is_active == True).offset(skip).limit(limit).all()
    return rooms


@router.post("/", response_model=RoomSchema)
async def create_room(
    room: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建房间"""
    # 检查服务器是否存在
    from app.models.server import Server
    server = db.query(Server).filter(Server.id == room.server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="服务器未找到")

    db_room = Room(**room.dict(), creator_id=current_user.id)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


@router.get("/{room_id}", response_model=RoomSchema)
async def get_room(room_id: int, db: Session = Depends(get_db)):
    """获取房间详情"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="房间未找到")
    return room


@router.put("/{room_id}", response_model=RoomSchema)
async def update_room(
    room_id: int,
    room_update: RoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新房间"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="房间未找到")

    # 检查权限（只有创建者可以更新）
    if room.creator_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="没有权限")

    for field, value in room_update.dict(exclude_unset=True).items():
        setattr(room, field, value)

    db.commit()
    db.refresh(room)
    return room


@router.post("/{room_id}/join", response_model=RoomJoinResponse)
async def join_room(
    room_id: int,
    join_request: RoomJoinRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """加入房间"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="房间未找到")

    if not room.is_active:
        return RoomJoinResponse(
            success=False,
            message="房间已关闭"
        )

    # 检查房间是否已满
    if room.current_players >= room.max_players:
        return RoomJoinResponse(
            success=False,
            message="房间已满"
        )

    # 检查密码
    if room.is_private and room.password != join_request.password:
        return RoomJoinResponse(
            success=False,
            message="密码错误"
        )

    # 检查是否已经在房间中
    existing_player = db.query(RoomPlayer).filter(
        RoomPlayer.room_id == room_id,
        RoomPlayer.user_id == current_user.id
    ).first()

    if existing_player:
        return RoomJoinResponse(
            success=False,
            message="您已经在房间中"
        )

    # 加入房间
    room_player = RoomPlayer(room_id=room_id, user_id=current_user.id)
    db.add(room_player)
    room.current_players += 1
    db.commit()

    return RoomJoinResponse(
        success=True,
        message="成功加入房间",
        room=room
    )


@router.post("/{room_id}/leave")
async def leave_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """离开房间"""
    room_player = db.query(RoomPlayer).filter(
        RoomPlayer.room_id == room_id,
        RoomPlayer.user_id == current_user.id
    ).first()

    if not room_player:
        raise HTTPException(status_code=404, detail="您不在此房间中")

    room = db.query(Room).filter(Room.id == room_id).first()
    if room:
        room.current_players = max(0, room.current_players - 1)
        db.delete(room_player)
        db.commit()

    return {"message": "已离开房间"}


@router.get("/{room_id}/players", response_model=List[RoomPlayerSchema])
async def get_room_players(room_id: int, db: Session = Depends(get_db)):
    """获取房间玩家列表"""
    players = db.query(RoomPlayer).filter(RoomPlayer.room_id == room_id).all()
    return players


@router.delete("/{room_id}")
async def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除房间"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="房间未找到")

    # 检查权限
    if room.creator_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="没有权限")

    # 删除所有房间玩家记录
    db.query(RoomPlayer).filter(RoomPlayer.room_id == room_id).delete()

    # 删除房间
    db.delete(room)
    db.commit()

    return {"message": "房间已删除"}
