"""
对话管理服务
"""
import json
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from langchain.schema import HumanMessage, AIMessage, SystemMessage

from ..models import Student, Conversation, Message, LearningPlan
from ..models.conversation import ConversationStatus, MessageRole
from .llm_service import LLMService
from .rag_service import RAGService
from ..core.database import get_db


class ConversationService:
    """对话管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.llm_service = LLMService()
        self.rag_service = RAGService()
    
    async def start_conversation(self, student_id: str, initial_message: str) -> Dict:
        """开始新对话"""
        # 获取学生信息
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise ValueError(f"Student {student_id} not found")
        
        # 创建新对话
        conversation = Conversation(
            student_id=student_id,
            status=ConversationStatus.ACTIVE,
            turn_count=0
        )
        self.db.add(conversation)
        self.db.commit()
        
        # 保存用户消息
        user_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=initial_message
        )
        self.db.add(user_message)
        
        # 生成初始评估提示
        student_info = student.to_dict()
        initial_prompt = self.llm_service.create_initial_assessment_prompt(student_info)
        
        # 构建消息历史
        messages = [
            SystemMessage(content=initial_prompt),
            HumanMessage(content=initial_message)
        ]
        
        # 获取AI响应
        ai_response, usage_info = await self.llm_service.get_response(messages)
        
        # 保存AI响应
        ai_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=ai_response,
            meta_data=json.dumps(usage_info)
        )
        self.db.add(ai_message)
        
        # 更新对话轮数
        conversation.turn_count = 1
        self.db.commit()
        
        return {
            "conversation_id": conversation.id,
            "response": ai_response,
            "status": conversation.status.value,
            "turn_count": conversation.turn_count
        }
    
    async def continue_conversation(self, conversation_id: str, user_message: str) -> Dict:
        """继续对话"""
        # 获取对话信息
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # 检查对话状态
        if conversation.status == ConversationStatus.COMPLETED:
            return {
                "error": "对话已结束",
                "status": conversation.status.value
            }
        
        # 获取学生信息
        student = conversation.student
        
        # 保存用户消息
        user_msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=user_message
        )
        self.db.add(user_msg)
        
        # 获取对话历史
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).all()
        
        # 构建对话历史
        conversation_history = []
        langchain_messages = []
        
        for msg in messages:
            conversation_history.append({
                "role": msg.role.value,
                "content": msg.content
            })
            
            if msg.role == MessageRole.USER:
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == MessageRole.ASSISTANT:
                langchain_messages.append(AIMessage(content=msg.content))
        
        # 增加轮数
        conversation.turn_count += 1
        
        # 根据对话阶段生成不同的提示
        if conversation.status == ConversationStatus.ACTIVE:
            # 创建继续对话的提示
            prompt, should_plan = self.llm_service.create_conversation_continuation_prompt(
                conversation_history,
                student.to_dict(),
                conversation.turn_count
            )
            
            # 如果应该进入计划制定阶段
            if should_plan:
                conversation.status = ConversationStatus.PLANNING
            
            # 添加系统提示
            langchain_messages.insert(0, SystemMessage(content=prompt))
            
        elif conversation.status == ConversationStatus.PLANNING:
            # 如果已经在计划制定阶段，检查是否应该生成计划
            if "好的" in user_message or "可以" in user_message or "开始" in user_message:
                # 生成学习计划
                plan_dict = await self._generate_learning_plan(student, conversation_history)
                
                # 保存学习计划
                learning_plan = LearningPlan(
                    student_id=student.id,
                    title=plan_dict.get("title", "个性化学习计划"),
                    description=plan_dict.get("description", ""),
                    objectives=plan_dict.get("objectives", []),
                    content=plan_dict.get("content", {}),
                    estimated_days=plan_dict.get("estimated_days", 30),
                    difficulty_level=plan_dict.get("difficulty_level", 3)
                )
                self.db.add(learning_plan)
                
                # 更新对话状态
                conversation.has_learning_plan = True
                conversation.status = ConversationStatus.COMPLETED
                
                # 存储学习计划到RAG
                self.rag_service.store_learning_plan(
                    student.id,
                    learning_plan.id,
                    plan_dict
                )
                
                # 生成计划完成的响应
                ai_response = f"""太好了！我已经为您制定了个性化的学习计划。

计划标题：{plan_dict.get('title')}
预计学习时长：{plan_dict.get('estimated_days')}天
难度级别：{plan_dict.get('difficulty_level')}/5

主要学习目标：
{chr(10).join([f"- {obj}" for obj in plan_dict.get('objectives', [])])}

现在您可以开始学习了！如果您需要开始具体的学习内容，请告诉我您想学习哪个部分。"""
                
            else:
                # 继续确认是否要制定计划
                prompt = "我理解您可能还有疑问。请告诉我您还想了解什么，或者如果您准备好了，我们可以开始制定学习计划。"
                langchain_messages.insert(0, SystemMessage(content=prompt))
                ai_response, usage_info = await self.llm_service.get_response(langchain_messages)
        
        else:
            # 已完成状态
            ai_response = "我们的初步评估对话已经完成。如果您想开始学习，请告诉我您想学习的具体内容。"
        
        # 如果还没有生成响应，获取AI响应
        if 'ai_response' not in locals():
            ai_response, usage_info = await self.llm_service.get_response(langchain_messages)
        else:
            usage_info = {}
        
        # 保存AI响应
        ai_msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=ai_response,
            meta_data=json.dumps(usage_info) if usage_info else None
        )
        self.db.add(ai_msg)
        
        self.db.commit()
        
        return {
            "conversation_id": conversation_id,
            "response": ai_response,
            "status": conversation.status.value,
            "turn_count": conversation.turn_count,
            "has_learning_plan": conversation.has_learning_plan
        }
    
    async def _generate_learning_plan(self, student: Student, conversation_history: List[Dict]) -> Dict:
        """生成学习计划"""
        # 分析对话历史，提取关键信息
        key_info = self.llm_service._analyze_conversation(conversation_history)
        
        # 创建对话总结
        conversation_summary = {
            "learning_goals": key_info.get("learning_goals", []),
            "background": key_info.get("background", ""),
            "preferred_style": key_info.get("preferred_style", ""),
            "available_time": key_info.get("available_time", ""),
            "current_level": key_info.get("current_level", ""),
            "challenges": key_info.get("challenges", [])
        }
        
        # 生成学习计划
        plan_dict = self.llm_service.create_learning_plan(
            student.to_dict(),
            conversation_summary
        )
        
        return plan_dict
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """获取对话历史"""
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).all()
        
        history = []
        for msg in messages:
            history.append({
                "id": msg.id,
                "role": msg.role.value,
                "content": msg.content,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            })
        
        return history
    
    def get_student_conversations(self, student_id: str) -> List[Dict]:
        """获取学生的所有对话"""
        conversations = self.db.query(Conversation).filter(
            Conversation.student_id == student_id
        ).order_by(Conversation.created_at.desc()).all()
        
        result = []
        for conv in conversations:
            result.append({
                "id": conv.id,
                "status": conv.status.value,
                "turn_count": conv.turn_count,
                "has_learning_plan": conv.has_learning_plan,
                "topic": conv.topic,
                "created_at": conv.created_at.isoformat() if conv.created_at else None,
                "updated_at": conv.updated_at.isoformat() if conv.updated_at else None
            })
        
        return result 