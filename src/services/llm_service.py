"""
LLM服务 - 处理与大语言模型的交互
"""
import json
from typing import List, Dict, Optional, Tuple
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_community.chat_models import ChatAnthropic
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.callbacks import get_openai_callback

from ..core.config import settings
from ..models.conversation import MessageRole


class LLMService:
    """LLM服务类"""
    
    def __init__(self):
        """初始化LLM服务"""
        # 根据配置选择不同的LLM提供商
        if settings.llm_provider == "openai":
            self.llm = ChatOpenAI(
                openai_api_key=settings.openai_api_key,
                openai_api_base=settings.openai_api_base,
                model_name=settings.openai_model,
                temperature=0.7,
                max_tokens=2000
            )
        elif settings.llm_provider == "azure":
            self.llm = AzureChatOpenAI(
                azure_endpoint=settings.azure_api_base,
                openai_api_key=settings.azure_api_key,
                openai_api_version=settings.azure_api_version,
                deployment_name=settings.azure_deployment_name,
                temperature=0.7,
                max_tokens=2000
            )
        elif settings.llm_provider == "deepseek":
            # DeepSeek使用OpenAI兼容的API
            self.llm = ChatOpenAI(
                openai_api_key=settings.deepseek_api_key,
                openai_api_base=settings.deepseek_api_base,
                model_name=settings.deepseek_model,
                temperature=0.7,
                max_tokens=2000
            )
        elif settings.llm_provider == "qwen":
            # Qwen使用OpenAI兼容的API
            self.llm = ChatOpenAI(
                openai_api_key=settings.qwen_api_key,
                openai_api_base=settings.qwen_api_base,
                model_name=settings.qwen_model,
                temperature=0.7,
                max_tokens=2000
            )
        elif settings.llm_provider == "claude":
            self.llm = ChatAnthropic(
                anthropic_api_key=settings.claude_api_key,
                model=settings.claude_model,
                temperature=0.7,
                max_tokens=2000
            )
        else:
            raise ValueError(f"不支持的LLM提供商: {settings.llm_provider}")
    
    def create_initial_assessment_prompt(self, student_info: Dict) -> str:
        """创建初始评估提示词"""
        prompt = f"""你是一位经验丰富的教育顾问，正在与一位新学生进行初次对话。

学生基本信息：
- 姓名：{student_info.get('name', '同学')}
- 年龄：{student_info.get('age', '未知')}
- 年级：{student_info.get('grade', '未知')}
- 兴趣：{', '.join(student_info.get('interests', []))}

你的任务是通过友好的对话了解学生的：
1. 学习背景和经历
2. 学习目标和动机
3. 学习风格和偏好
4. 当前的知识水平
5. 可用的学习时间

请用温暖、鼓励的语气开始对话，先做简单的自我介绍，然后询问一个开放性问题。
记住要循序渐进，不要一次问太多问题。"""
        
        return prompt
    
    def create_conversation_continuation_prompt(self, 
                                              conversation_history: List[Dict],
                                              student_info: Dict,
                                              turn_count: int) -> Tuple[str, bool]:
        """
        创建对话继续的提示词
        返回：(提示词, 是否应该进入学习计划制定阶段)
        """
        should_plan = False
        
        # 分析对话历史，提取关键信息
        key_info = self._analyze_conversation(conversation_history)
        
        # 判断是否应该进入学习计划制定阶段
        if turn_count >= settings.min_conversation_turns:
            if self._has_sufficient_info(key_info):
                should_plan = True
        
        if should_plan:
            prompt = f"""基于之前的对话，你已经充分了解了学生的情况。

学生关键信息总结：
{json.dumps(key_info, ensure_ascii=False, indent=2)}

现在请你：
1. 简要总结你对学生情况的理解
2. 询问学生是否准备好开始制定个性化的学习计划
3. 如果学生同意，告诉他们你将为他们设计一个适合的学习方案"""
        else:
            # 根据已收集的信息，决定下一个问题
            prompt = self._create_next_question_prompt(conversation_history, key_info, student_info)
        
        return prompt, should_plan
    
    def create_learning_plan(self, student_info: Dict, conversation_summary: Dict) -> Dict:
        """创建学习计划"""
        prompt = f"""基于学生信息和对话总结，请创建一个详细的个性化学习计划。

学生信息：
{json.dumps(student_info, ensure_ascii=False, indent=2)}

对话总结：
{json.dumps(conversation_summary, ensure_ascii=False, indent=2)}

请创建一个结构化的学习计划，包含以下内容：
1. 学习目标（具体、可衡量）
2. 学习路径（分阶段的学习内容）
3. 时间安排（每个阶段的预计时长）
4. 学习资源推荐
5. 评估方式

请以JSON格式返回学习计划。"""
        
        response = self.llm.invoke(prompt)
        
        # 解析响应，提取JSON
        try:
            plan_text = response.content
            # 尝试从响应中提取JSON
            import re
            json_match = re.search(r'\{.*\}', plan_text, re.DOTALL)
            if json_match:
                plan_dict = json.loads(json_match.group())
            else:
                # 如果没有找到JSON，构造一个基本的计划结构
                plan_dict = {
                    "title": "个性化学习计划",
                    "objectives": ["待定"],
                    "content": {"stages": []},
                    "estimated_days": 30,
                    "resources": []
                }
        except:
            plan_dict = {
                "title": "个性化学习计划",
                "description": plan_text,
                "objectives": [],
                "content": {},
                "estimated_days": 30
            }
        
        return plan_dict
    
    def create_teaching_prompt(self, 
                             topic: str,
                             student_level: str,
                             learning_style: str,
                             previous_context: Optional[str] = None) -> str:
        """创建教学提示词"""
        prompt = f"""你是一位采用苏格拉底式教学法的优秀教师。

教学主题：{topic}
学生水平：{student_level}
学习风格：{learning_style}
{f'之前的学习内容：{previous_context}' if previous_context else ''}

请使用启发式教学方法：
1. 不要直接给出答案，而是通过提问引导学生思考
2. 从学生已知的概念出发，逐步引导到新知识
3. 鼓励学生主动思考和提问
4. 适时给予正面反馈和鼓励
5. 根据学生的回答调整教学节奏

请开始你的教学，记住要循序渐进，保持互动性。"""
        
        return prompt
    
    async def get_response(self, messages: List[BaseMessage]) -> Tuple[str, Dict]:
        """获取LLM响应"""
        try:
            # 对于支持回调的模型，使用回调获取token信息
            if settings.llm_provider in ["openai", "azure", "deepseek", "qwen"]:
                with get_openai_callback() as cb:
                    response = await self.llm.ainvoke(messages)
                    
                    usage_info = {
                        "total_tokens": cb.total_tokens,
                        "prompt_tokens": cb.prompt_tokens,
                        "completion_tokens": cb.completion_tokens,
                        "total_cost": cb.total_cost
                    }
            else:
                # Claude等不支持OpenAI回调的模型
                response = await self.llm.ainvoke(messages)
                usage_info = {
                    "total_tokens": 0,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_cost": 0
                }
                
            return response.content, usage_info
        except Exception as e:
            print(f"LLM调用错误: {str(e)}")
            raise
    
    def _analyze_conversation(self, conversation_history: List[Dict]) -> Dict:
        """分析对话历史，提取关键信息"""
        # 这里可以使用LLM来分析，或者使用规则提取
        key_info = {
            "learning_goals": [],
            "background": "",
            "preferred_style": "",
            "available_time": "",
            "current_level": "",
            "challenges": []
        }
        
        # 简单的关键词提取（实际应用中可以使用更复杂的NLP方法）
        for msg in conversation_history:
            content = msg.get("content", "").lower()
            
            if "目标" in content or "想学" in content:
                key_info["learning_goals"].append(content)
            
            if "基础" in content or "学过" in content:
                key_info["background"] += content + " "
            
            if "喜欢" in content or "偏好" in content:
                key_info["preferred_style"] += content + " "
        
        return key_info
    
    def _has_sufficient_info(self, key_info: Dict) -> bool:
        """判断是否已收集足够信息"""
        required_fields = ["learning_goals", "background", "current_level"]
        
        for field in required_fields:
            if not key_info.get(field):
                return False
        
        return True
    
    def _create_next_question_prompt(self, 
                                   conversation_history: List[Dict],
                                   key_info: Dict,
                                   student_info: Dict) -> str:
        """创建下一个问题的提示词"""
        # 根据已收集的信息决定问什么
        missing_info = []
        
        if not key_info.get("learning_goals"):
            missing_info.append("学习目标")
        if not key_info.get("background"):
            missing_info.append("学习背景")
        if not key_info.get("current_level"):
            missing_info.append("当前水平")
        if not key_info.get("available_time"):
            missing_info.append("可用学习时间")
        
        prompt = f"""继续与学生{student_info.get('name', '同学')}的对话。

已收集信息：
{json.dumps(key_info, ensure_ascii=False, indent=2)}

还需要了解：{', '.join(missing_info)}

请基于之前的对话，自然地询问下一个问题。保持友好和鼓励的语气，一次只问一个问题。
如果学生的回答不够具体，可以追问细节。"""
        
        return prompt 