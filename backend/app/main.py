from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import create_tables
from app.api import auth, servers, mods, rooms

# 创建FastAPI应用
app = FastAPI(
    title="L4D2 Management Platform",
    description="L4D2服务器管理平台API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(servers.router, prefix="/api/servers", tags=["服务器管理"])
app.include_router(mods.router, prefix="/api/mods", tags=["Mod管理"])
app.include_router(rooms.router, prefix="/api/rooms", tags=["房间管理"])

# 创建数据库表
@app.on_event("startup")
async def startup_event():
    create_tables()

@app.get("/")
async def root():
    return {"message": "L4D2 Management Platform API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
