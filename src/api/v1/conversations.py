"""
对话API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...schemas.conversation import (
    StartConversationRequest,
    ContinueConversationRequest,
    ConversationResponse,
    ConversationHistoryResponse,
    ConversationListResponse,
    MessageResponse,
    ConversationListItem
)
from ...services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/start", response_model=ConversationResponse)
async def start_conversation(
    request: StartConversationRequest,
    db: Session = Depends(get_db)
):
    """开始新对话"""
    service = ConversationService(db)
    
    try:
        result = await service.start_conversation(
            request.student_id,
            request.initial_message
        )
        return ConversationResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话启动失败: {str(e)}")


@router.post("/{conversation_id}/continue", response_model=ConversationResponse)
async def continue_conversation(
    conversation_id: str,
    request: ContinueConversationRequest,
    db: Session = Depends(get_db)
):
    """继续对话"""
    service = ConversationService(db)
    
    try:
        result = await service.continue_conversation(
            conversation_id,
            request.message
        )
        return ConversationResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话继续失败: {str(e)}")


@router.get("/{conversation_id}/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """获取对话历史"""
    service = ConversationService(db)
    
    try:
        messages = service.get_conversation_history(conversation_id)
        return ConversationHistoryResponse(
            messages=[MessageResponse(**msg) for msg in messages],
            total=len(messages)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对话历史失败: {str(e)}")


@router.get("/student/{student_id}", response_model=ConversationListResponse)
async def get_student_conversations(
    student_id: str,
    db: Session = Depends(get_db)
):
    """获取学生的所有对话"""
    service = ConversationService(db)
    
    try:
        conversations = service.get_student_conversations(student_id)
        return ConversationListResponse(
            conversations=[ConversationListItem(**conv) for conv in conversations],
            total=len(conversations)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对话列表失败: {str(e)}") 