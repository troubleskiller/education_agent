"""
教学相关的Pydantic模式
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class StartTeachingRequest(BaseModel):
    """开始教学请求"""
    student_id: str = Field(..., description="学生ID")
    topic: str = Field(..., description="教学主题")
    learning_plan_id: Optional[str] = Field(None, description="学习计划ID")


class ContinueTeachingRequest(BaseModel):
    """继续教学请求"""
    session_id: str = Field(..., description="教学会话ID")
    student_response: str = Field(..., description="学生回答")
    conversation_history: List[Dict[str, str]] = Field(..., description="对话历史")


class TeachingSessionResponse(BaseModel):
    """教学会话响应"""
    session_id: str
    response: str
    context: Dict[str, Any]
    materials_used: int


class TeachingContinuationResponse(BaseModel):
    """教学继续响应"""
    response: str
    analysis: Dict[str, Any]
    strategy: str
    mastery_level: int


class LearningRecommendation(BaseModel):
    """学习推荐"""
    topic: str
    reason: str


class PeerLearning(BaseModel):
    """同伴学习"""
    student_id: str
    name: str
    grade: str
    similarity_score: Optional[float] = None


class LearningRecommendationsResponse(BaseModel):
    """学习建议响应"""
    next_topics: List[LearningRecommendation]
    review_topics: List[LearningRecommendation]
    peer_learning: List[PeerLearning]
    study_tips: List[str] 