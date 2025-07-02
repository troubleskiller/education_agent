"""
学生数据模型
"""
from sqlalchemy import Column, String, Integer, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..core.database import Base


class Student(Base):
    """学生信息模型"""
    __tablename__ = "students"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    age = Column(Integer)
    grade = Column(String(50))
    
    # 学生兴趣爱好，存储为JSON数组
    interests = Column(JSON, default=list)
    
    # 学生背景信息
    background = Column(Text)
    
    # 学习目标
    learning_goals = Column(Text)
    
    # 学习风格偏好
    learning_style = Column(String(50))
    
    # 当前知识水平评估
    knowledge_level = Column(JSON, default=dict)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    conversations = relationship("Conversation", back_populates="student", cascade="all, delete-orphan")
    learning_plans = relationship("LearningPlan", back_populates="student", cascade="all, delete-orphan")
    learning_progress = relationship("LearningProgress", back_populates="student", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Student(id={self.id}, name={self.name}, grade={self.grade})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "grade": self.grade,
            "interests": self.interests or [],
            "background": self.background,
            "learning_goals": self.learning_goals,
            "learning_style": self.learning_style,
            "knowledge_level": self.knowledge_level or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 