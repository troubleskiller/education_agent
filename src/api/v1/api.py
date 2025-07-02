"""
API v1 主路由
"""
from fastapi import APIRouter

from .students import router as students_router
from .conversations import router as conversations_router
from .teaching import router as teaching_router

api_router = APIRouter()

# 包含所有子路由
api_router.include_router(students_router)
api_router.include_router(conversations_router)
api_router.include_router(teaching_router) 