"""
对话数据模型
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from ..core.database import Base


class ConversationStatus(str, enum.Enum):
    """对话状态枚举"""
    ACTIVE = "active"
    PLANNING = "planning"  # 进入学习计划制定阶段
    COMPLETED = "completed"
    ARCHIVED = "archived"


class MessageRole(str, enum.Enum):
    """消息角色枚举"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Conversation(Base):
    """对话模型"""
    __tablename__ = "conversations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id"), nullable=False)
    
    # 对话状态
    status = Column(Enum(ConversationStatus), default=ConversationStatus.ACTIVE)
    
    # 对话轮数
    turn_count = Column(Integer, default=0)
    
    # 是否已生成学习计划
    has_learning_plan = Column(Boolean, default=False)
    
    # 对话主题
    topic = Column(String(200))
    
    # 对话总结
    summary = Column(Text)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    student = relationship("Student", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, student_id={self.student_id}, status={self.status})>"


class Message(Base):
    """消息模型"""
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    
    # 消息角色
    role = Column(Enum(MessageRole), nullable=False)
    
    # 消息内容
    content = Column(Text, nullable=False)
    
    # 消息元数据（如思维链、情感分析等）
    meta_data = Column(Text)  # JSON string - 改名避免与SQLAlchemy保留字冲突
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, conversation_id={self.conversation_id})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role.value if self.role else None,
            "content": self.content,
            "metadata": self.meta_data,  # 保持API兼容性
            "created_at": self.created_at.isoformat() if self.created_at else None
        } 