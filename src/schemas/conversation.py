"""
对话相关的Pydantic模式
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class StartConversationRequest(BaseModel):
    """开始对话请求"""
    student_id: str = Field(..., description="学生ID")
    initial_message: str = Field(..., description="初始消息")


class ContinueConversationRequest(BaseModel):
    """继续对话请求"""
    message: str = Field(..., description="用户消息")


class ConversationResponse(BaseModel):
    """对话响应"""
    conversation_id: str
    response: str
    status: str
    turn_count: int
    has_learning_plan: Optional[bool] = False
    error: Optional[str] = None


class MessageResponse(BaseModel):
    """消息响应"""
    id: str
    role: str
    content: str
    created_at: Optional[datetime] = None


class ConversationHistoryResponse(BaseModel):
    """对话历史响应"""
    messages: List[MessageResponse]
    total: int


class ConversationListItem(BaseModel):
    """对话列表项"""
    id: str
    status: str
    turn_count: int
    has_learning_plan: bool
    topic: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ConversationListResponse(BaseModel):
    """对话列表响应"""
    conversations: List[ConversationListItem]
    total: int 