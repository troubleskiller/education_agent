"""
教学API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...schemas.teaching import (
    StartTeachingRequest,
    ContinueTeachingRequest,
    TeachingSessionResponse,
    TeachingContinuationResponse,
    LearningRecommendationsResponse
)
from ...services.teaching_service import TeachingService

router = APIRouter(prefix="", tags=["teaching"])


@router.post("/start", response_model=TeachingSessionResponse)
async def start_teaching_session(
    request: StartTeachingRequest,
    db: Session = Depends(get_db)
):
    """开始教学会话"""
    service = TeachingService(db)
    
    try:
        result = await service.start_teaching_session(
            student_id=request.student_id,
            topic=request.topic,
            learning_plan_id=request.learning_plan_id
        )
        return TeachingSessionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动教学会话失败: {str(e)}")


@router.post("/continue", response_model=TeachingContinuationResponse)
async def continue_teaching(
    request: ContinueTeachingRequest,
    db: Session = Depends(get_db)
):
    """继续教学对话"""
    service = TeachingService(db)
    
    try:
        result = await service.continue_teaching(
            session_id=request.session_id,
            student_response=request.student_response,
            conversation_history=request.conversation_history
        )
        return TeachingContinuationResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"继续教学失败: {str(e)}")


@router.get("/{student_id}/recommendations", response_model=LearningRecommendationsResponse)
async def get_learning_recommendations(
    student_id: str,
    db: Session = Depends(get_db)
):
    """获取学习建议"""
    service = TeachingService(db)
    
    try:
        recommendations = await service.get_learning_recommendations(student_id)
        return LearningRecommendationsResponse(**recommendations)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取学习建议失败: {str(e)}") 