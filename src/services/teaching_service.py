"""
启发式教学服务
"""
import json
from typing import List, Dict, Optional

from langchain_core.messages import BaseMessage
from sqlalchemy.orm import Session
from langchain.schema import HumanMessage, AIMessage, SystemMessage

from ..models import Student, LearningPlan, LearningProgress
from .llm_service import LLMService
from .rag_service import RAGService


class TeachingService:
    """启发式教学服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.llm_service = LLMService()
        self.rag_service = RAGService()
    
    async def start_teaching_session(self, 
                                   student_id: str, 
                                   topic: str,
                                   learning_plan_id: Optional[str] = None) -> Dict:
        """开始教学会话"""
        # 获取学生信息
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise ValueError(f"Student {student_id} not found")
        
        # 获取学习计划（如果有）
        learning_plan = None
        if learning_plan_id:
            learning_plan = self.db.query(LearningPlan).filter(
                LearningPlan.id == learning_plan_id,
                LearningPlan.student_id == student_id
            ).first()
        
        # 从RAG获取相关教学材料
        teaching_materials = self.rag_service.search_teaching_materials(
            query=topic,
            level=student.grade,
            k=3
        )
        
        # 获取学生的学习进度（如果有）
        progress = None
        if learning_plan:
            progress = self.db.query(LearningProgress).filter(
                LearningProgress.student_id == student_id,
                LearningProgress.learning_plan_id == learning_plan_id
            ).order_by(LearningProgress.created_at.desc()).first()
        
        # 构建教学上下文
        context = self._build_teaching_context(
            student,
            topic,
            learning_plan,
            progress,
            teaching_materials
        )
        
        # 创建教学提示
        teaching_prompt = self.llm_service.create_teaching_prompt(
            topic=topic,
            student_level=student.grade or "初级",
            learning_style=student.learning_style or "视觉型",
            previous_context=context.get("previous_learning")
        )
        
        # 获取初始教学响应
        messages = [SystemMessage(content=teaching_prompt)]
        response, usage_info = await self.llm_service.get_response(messages)
        
        return {
            "session_id": f"teach_{student_id}_{topic}",
            "response": response,
            "context": context,
            "materials_used": len(teaching_materials)
        }
    
    async def continue_teaching(self,
                              session_id: str,
                              student_response: str,
                              conversation_history: List[Dict]) -> Dict:
        """继续教学对话"""
        # 解析session_id获取信息
        parts = session_id.split("_")
        student_id = parts[1]
        topic = "_".join(parts[2:])
        
        # 获取学生信息
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise ValueError(f"Student {student_id} not found")
        
        # 分析学生的回答
        analysis = self._analyze_student_response(student_response, topic)
        
        # 根据分析结果决定教学策略
        teaching_strategy = self._determine_teaching_strategy(analysis, conversation_history)
        
        # 构建消息历史
        messages = self._build_message_history(conversation_history)
        
        # 添加最新的学生消息
        messages.append(HumanMessage(content=student_response))
        
        # 创建系统提示以指导教学方向
        system_prompt = self._create_adaptive_teaching_prompt(
            topic,
            analysis,
            teaching_strategy,
            student
        )
        
        # 插入系统提示
        messages.insert(0, SystemMessage(content=system_prompt))
        
        # 获取AI响应
        response, usage_info = await self.llm_service.get_response(messages)
        
        # 如果检测到学生掌握了概念，更新进度
        if analysis.get("mastery_level", 0) >= 4:
            await self._update_learning_progress(student_id, topic, analysis)
        
        return {
            "response": response,
            "analysis": analysis,
            "strategy": teaching_strategy,
            "mastery_level": analysis.get("mastery_level", 0)
        }
    
    def _build_teaching_context(self,
                              student: Student,
                              topic: str,
                              learning_plan: Optional[LearningPlan],
                              progress: Optional[LearningProgress],
                              materials: List[Dict]) -> Dict:
        """构建教学上下文"""
        context = {
            "student_name": student.name,
            "student_level": student.grade,
            "learning_style": student.learning_style,
            "topic": topic
        }
        
        if learning_plan:
            context["learning_plan"] = {
                "title": learning_plan.title,
                "current_objectives": learning_plan.objectives[:3] if learning_plan.objectives else []
            }
        
        if progress:
            context["previous_learning"] = {
                "last_module": progress.current_module,
                "progress": progress.progress_percentage,
                "challenges": progress.challenges or []
            }
        
        if materials:
            context["reference_materials"] = [
                {
                    "content": mat["content"][:200] + "...",
                    "source": mat.get("metadata", {}).get("source", "知识库")
                }
                for mat in materials[:2]
            ]
        
        return context
    
    def _analyze_student_response(self, response: str, topic: str) -> Dict:
        """分析学生回答"""
        # 这里可以使用更复杂的NLP分析
        # 简单实现：基于关键词和长度判断
        
        analysis = {
            "response_length": len(response),
            "contains_question": "？" in response or "?" in response,
            "confidence_indicators": [],
            "confusion_indicators": [],
            "mastery_level": 3  # 1-5级
        }
        
        # 检查理解程度指标
        understanding_keywords = ["明白", "懂了", "原来如此", "我知道", "理解"]
        confusion_keywords = ["不懂", "不明白", "为什么", "怎么", "能再解释"]
        
        for keyword in understanding_keywords:
            if keyword in response:
                analysis["confidence_indicators"].append(keyword)
                analysis["mastery_level"] = min(5, analysis["mastery_level"] + 1)
        
        for keyword in confusion_keywords:
            if keyword in response:
                analysis["confusion_indicators"].append(keyword)
                analysis["mastery_level"] = max(1, analysis["mastery_level"] - 1)
        
        # 如果回答很短，可能需要更多引导
        if analysis["response_length"] < 10:
            analysis["needs_encouragement"] = True
        
        return analysis
    
    def _determine_teaching_strategy(self, analysis: Dict, history: List[Dict]) -> str:
        """确定教学策略"""
        if analysis.get("confusion_indicators"):
            return "clarify"  # 澄清解释
        elif analysis.get("contains_question"):
            return "answer_question"  # 回答问题
        elif analysis.get("mastery_level", 0) >= 4:
            return "advance"  # 进入更深层次
        elif analysis.get("needs_encouragement"):
            return "encourage"  # 鼓励引导
        else:
            return "elaborate"  # 详细阐述
    
    def _create_adaptive_teaching_prompt(self,
                                       topic: str,
                                       analysis: Dict,
                                       strategy: str,
                                       student: Student) -> str:
        """创建自适应教学提示"""
        base_prompt = f"你正在教授{student.name}关于{topic}的知识。"
        
        strategy_prompts = {
            "clarify": """
学生似乎对某些概念感到困惑。请：
1. 用更简单的语言重新解释核心概念
2. 使用生活中的类比帮助理解
3. 将复杂概念分解成小步骤
4. 确认学生理解后再继续
""",
            "answer_question": """
学生提出了问题。请：
1. 直接回答学生的具体问题
2. 确保答案清晰易懂
3. 提供相关例子
4. 询问是否还有其他疑问
""",
            "advance": """
学生已经掌握了当前概念。请：
1. 表扬学生的理解
2. 引入相关的更深层次概念
3. 建立新旧知识之间的联系
4. 保持循序渐进
""",
            "encourage": """
学生需要更多鼓励和引导。请：
1. 给予积极的反馈
2. 提出引导性的简单问题
3. 降低问题难度
4. 创造轻松的学习氛围
""",
            "elaborate": """
继续深入讲解。请：
1. 提供更多细节和例子
2. 通过提问检查理解程度
3. 鼓励学生主动思考
4. 保持互动性
"""
        }
        
        return base_prompt + "\n" + strategy_prompts.get(strategy, strategy_prompts["elaborate"])
    
    def _build_message_history(self, history: List[Dict]) -> List[BaseMessage]:
        """构建消息历史"""
        messages = []
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        return messages
    
    async def _update_learning_progress(self, student_id: str, topic: str, analysis: Dict):
        """更新学习进度"""
        # 查找相关的学习计划
        active_plan = self.db.query(LearningPlan).filter(
            LearningPlan.student_id == student_id,
            LearningPlan.is_active == True
        ).first()
        
        if active_plan:
            # 创建或更新进度记录
            progress = self.db.query(LearningProgress).filter(
                LearningProgress.student_id == student_id,
                LearningProgress.learning_plan_id == active_plan.id
            ).first()
            
            if not progress:
                progress = LearningProgress(
                    student_id=student_id,
                    learning_plan_id=active_plan.id,
                    current_module=topic,
                    progress_percentage=0.0
                )
                self.db.add(progress)
            
            # 更新进度
            progress.current_module = topic
            progress.mastery_level = analysis.get("mastery_level", 3)
            
            # 简单计算进度百分比（实际应用中应该更精确）
            if progress.mastery_level >= 4:
                progress.progress_percentage = min(100, progress.progress_percentage + 10)
            
            self.db.commit()
    
    async def get_learning_recommendations(self, student_id: str) -> Dict:
        """获取学习建议"""
        # 获取学生信息和学习历史
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise ValueError(f"Student {student_id} not found")
        
        # 获取学习进度
        progress_records = self.db.query(LearningProgress).filter(
            LearningProgress.student_id == student_id
        ).all()
        
        # 查找相似学生
        similar_students = self.rag_service.find_similar_students(student_id, k=3)
        
        # 基于进度和相似学生生成建议
        recommendations = {
            "next_topics": [],
            "review_topics": [],
            "peer_learning": similar_students,
            "study_tips": []
        }
        
        # 分析进度，确定需要复习和推进的主题
        for progress in progress_records:
            if progress.mastery_level < 3:
                recommendations["review_topics"].append({
                    "topic": progress.current_module,
                    "reason": "需要加强理解"
                })
            elif progress.mastery_level >= 4:
                # 这里可以基于知识图谱推荐下一个主题
                recommendations["next_topics"].append({
                    "topic": f"{progress.current_module} - 进阶",
                    "reason": "已掌握基础"
                })
        
        # 添加学习建议
        if student.learning_style == "视觉型":
            recommendations["study_tips"].append("建议使用图表和思维导图辅助学习")
        elif student.learning_style == "听觉型":
            recommendations["study_tips"].append("建议通过讲解和讨论来加深理解")
        
        return recommendations 