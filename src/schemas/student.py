"""
学生相关的Pydantic模式
"""
from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field


class StudentBase(BaseModel):
    """学生基础模式"""
    name: str = Field(..., description="学生姓名")
    age: Optional[int] = Field(None, description="年龄")
    grade: Optional[str] = Field(None, description="年级")
    interests: Optional[List[str]] = Field(default_factory=list, description="兴趣爱好")


class StudentCreate(StudentBase):
    """创建学生模式"""
    background: Optional[str] = Field(None, description="背景信息")
    learning_goals: Optional[str] = Field(None, description="学习目标")
    learning_style: Optional[str] = Field(None, description="学习风格")


class StudentUpdate(BaseModel):
    """更新学生模式"""
    name: Optional[str] = None
    age: Optional[int] = None
    grade: Optional[str] = None
    interests: Optional[List[str]] = None
    background: Optional[str] = None
    learning_goals: Optional[str] = None
    learning_style: Optional[str] = None
    knowledge_level: Optional[Dict] = None


class StudentResponse(StudentBase):
    """学生响应模式"""
    id: str
    background: Optional[str] = None
    learning_goals: Optional[str] = None
    learning_style: Optional[str] = None
    knowledge_level: Optional[Dict] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class StudentListResponse(BaseModel):
    """学生列表响应模式"""
    students: List[StudentResponse]
    total: int 