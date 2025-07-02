"""
学习计划数据模型
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..core.database import Base


class LearningPlan(Base):
    """学习计划模型"""
    __tablename__ = "learning_plans"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id"), nullable=False)
    
    # 计划标题
    title = Column(String(200), nullable=False)
    
    # 计划描述
    description = Column(Text)
    
    # 学习目标
    objectives = Column(JSON)  # 存储为JSON数组
    
    # 计划内容（详细的学习路径）
    content = Column(JSON)  # 存储为JSON对象
    
    # 预计完成时间（天）
    estimated_days = Column(Integer)
    
    # 难度级别 (1-5)
    difficulty_level = Column(Integer, default=3)
    
    # 是否激活
    is_active = Column(Boolean, default=True)
    
    # 完成状态
    is_completed = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # 关系
    student = relationship("Student", back_populates="learning_plans")
    progress_records = relationship("LearningProgress", back_populates="learning_plan", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<LearningPlan(id={self.id}, title={self.title}, student_id={self.student_id})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "student_id": self.student_id,
            "title": self.title,
            "description": self.description,
            "objectives": self.objectives or [],
            "content": self.content or {},
            "estimated_days": self.estimated_days,
            "difficulty_level": self.difficulty_level,
            "is_active": self.is_active,
            "is_completed": self.is_completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class LearningProgress(Base):
    """学习进度模型"""
    __tablename__ = "learning_progress"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id"), nullable=False)
    learning_plan_id = Column(String(36), ForeignKey("learning_plans.id"), nullable=False)
    
    # 当前学习章节/模块
    current_module = Column(String(200))
    
    # 完成进度 (0-100)
    progress_percentage = Column(Float, default=0.0)
    
    # 学习笔记
    notes = Column(Text)
    
    # 遇到的问题
    challenges = Column(JSON)  # 存储为JSON数组
    
    # 掌握程度评估 (1-5)
    mastery_level = Column(Integer)
    
    # 学习时长（分钟）
    study_duration_minutes = Column(Integer, default=0)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    student = relationship("Student", back_populates="learning_progress")
    learning_plan = relationship("LearningPlan", back_populates="progress_records")
    
    def __repr__(self):
        return f"<LearningProgress(id={self.id}, student_id={self.student_id}, progress={self.progress_percentage}%)>" 