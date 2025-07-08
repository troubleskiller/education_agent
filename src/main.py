"""
FastAPI 主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .core.config import settings
from .core.database import engine, Base
from .api.v1 import students, conversations, teaching

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title="教育智能体系统",
    description="基于大语言模型的个性化教育系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(students.router, prefix="/api/v1/students", tags=["students"])
app.include_router(conversations.router, prefix="/api/v1/conversations", tags=["conversations"])
app.include_router(teaching.router, prefix="/api/v1/teaching", tags=["teaching"])

# 挂载静态文件目录
static_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# 根路径返回前端页面
@app.get("/")
async def read_index():
    index_path = os.path.join(static_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "欢迎使用教育智能体系统"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True) 