"""
RAG服务 - 管理向量数据库和知识检索
"""
import os
import json
from typing import List, Dict, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document
import chromadb

from ..core.config import settings


class RAGService:
    """RAG服务类"""
    
    def __init__(self):
        """初始化RAG服务"""
        # 初始化嵌入模型
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.openai_api_base
        )
        
        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        )
        
        # 初始化ChromaDB云客户端
        self.chroma_client = chromadb.CloudClient(
            api_key=settings.chroma_api_key,
            tenant=settings.chroma_tenant,
            database=settings.chroma_database
        )
        
        # 创建不同的集合
        self._init_collections()
    
    def _init_collections(self):
        """初始化向量数据库集合"""
        # 学习计划集合
        self.learning_plans_collection = "learning_plans"
        
        # 教学材料集合
        self.teaching_materials_collection = "teaching_materials"
        
        # 学生档案集合
        self.student_profiles_collection = "student_profiles"
        
        # 确保集合存在
        try:
            self.chroma_client.get_or_create_collection(name=self.learning_plans_collection)
            self.chroma_client.get_or_create_collection(name=self.teaching_materials_collection)
            self.chroma_client.get_or_create_collection(name=self.student_profiles_collection)
        except Exception as e:
            print(f"创建集合时出错: {e}")
    
    def store_learning_plan(self, student_id: str, plan_id: str, plan_content: Dict):
        """存储学习计划到向量数据库"""
        # 将学习计划转换为文本
        plan_text = self._format_learning_plan(plan_content)
        
        # 创建文档
        documents = [
            Document(
                page_content=plan_text,
                metadata={
                    "student_id": student_id,
                    "plan_id": plan_id,
                    "type": "learning_plan",
                    "title": plan_content.get("title", ""),
                    "created_at": plan_content.get("created_at", "")
                }
            )
        ]
        
        # 分割文本
        splits = self.text_splitter.split_documents(documents)
        
        # 创建或获取向量存储
        vectorstore = Chroma(
            client=self.chroma_client,
            collection_name=self.learning_plans_collection,
            embedding_function=self.embeddings
        )
        
        # 添加文档
        vectorstore.add_documents(splits)
    
    def search_learning_plans(self, query: str, student_id: Optional[str] = None, k: int = 5) -> List[Dict]:
        """搜索学习计划"""
        vectorstore = Chroma(
            client=self.chroma_client,
            collection_name=self.learning_plans_collection,
            embedding_function=self.embeddings
        )
        
        # 构建过滤器
        filter_dict = {}
        if student_id:
            filter_dict["student_id"] = student_id
        
        # 执行搜索
        results = vectorstore.similarity_search(
            query=query,
            k=k,
            filter=filter_dict if filter_dict else None
        )
        
        # 格式化结果
        formatted_results = []
        for doc in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": getattr(doc, "score", None)
            })
        
        return formatted_results
    
    def store_teaching_material(self, material_id: str, content: str, metadata: Dict):
        """存储教学材料"""
        documents = [
            Document(
                page_content=content,
                metadata={
                    "material_id": material_id,
                    "type": "teaching_material",
                    **metadata
                }
            )
        ]
        
        # 分割文本
        splits = self.text_splitter.split_documents(documents)
        
        # 创建或获取向量存储
        vectorstore = Chroma(
            client=self.chroma_client,
            collection_name=self.teaching_materials_collection,
            embedding_function=self.embeddings
        )
        
        # 添加文档
        vectorstore.add_documents(splits)
    
    def search_teaching_materials(self, query: str, subject: Optional[str] = None, 
                                level: Optional[str] = None, k: int = 5) -> List[Dict]:
        """搜索教学材料"""
        vectorstore = Chroma(
            client=self.chroma_client,
            collection_name=self.teaching_materials_collection,
            embedding_function=self.embeddings
        )
        
        # 构建过滤器
        filter_dict = {}
        if subject:
            filter_dict["subject"] = subject
        if level:
            filter_dict["level"] = level
        
        # 执行搜索
        results = vectorstore.similarity_search(
            query=query,
            k=k,
            filter=filter_dict if filter_dict else None
        )
        
        # 格式化结果
        formatted_results = []
        for doc in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })
        
        return formatted_results
    
    def update_student_profile_embedding(self, student_id: str, profile_data: Dict):
        """更新学生档案的向量表示"""
        # 格式化学生档案信息
        profile_text = self._format_student_profile(profile_data)
        
        documents = [
            Document(
                page_content=profile_text,
                metadata={
                    "student_id": student_id,
                    "type": "student_profile",
                    "name": profile_data.get("name", ""),
                    "grade": profile_data.get("grade", ""),
                    "updated_at": profile_data.get("updated_at", "")
                }
            )
        ]
        
        # 创建或获取向量存储
        vectorstore = Chroma(
            client=self.chroma_client,
            collection_name=self.student_profiles_collection,
            embedding_function=self.embeddings
        )
        
        # 先删除旧的档案（如果存在）
        try:
            collection = self.chroma_client.get_collection(self.student_profiles_collection)
            # 获取该学生的所有文档ID
            results = collection.get(where={"student_id": student_id})
            if results['ids']:
                collection.delete(ids=results['ids'])
        except:
            pass
        
        # 添加新档案
        vectorstore.add_documents(documents)
    
    def find_similar_students(self, student_id: str, k: int = 3) -> List[Dict]:
        """查找相似的学生（用于推荐学习伙伴或参考案例）"""
        vectorstore = Chroma(
            client=self.chroma_client,
            collection_name=self.student_profiles_collection,
            embedding_function=self.embeddings
        )
        
        # 先获取当前学生的档案
        collection = self.chroma_client.get_collection(self.student_profiles_collection)
        current_student_results = collection.get(where={"student_id": student_id})
        
        if not current_student_results['documents']:
            return []
        
        # 使用第一个文档进行相似度搜索
        query_text = current_student_results['documents'][0]
        
        # 搜索相似学生
        results = vectorstore.similarity_search(
            query=query_text,
            k=k + 1,  # 多搜索一个，因为会包含自己
        )
        
        # 格式化结果，排除自己
        similar_students = []
        for doc in results:
            if doc.metadata.get("student_id") != student_id:
                similar_students.append({
                    "student_id": doc.metadata.get("student_id"),
                    "name": doc.metadata.get("name"),
                    "grade": doc.metadata.get("grade"),
                    "similarity_score": getattr(doc, "score", None)
                })
                if len(similar_students) >= k:
                    break
        
        return similar_students
    
    def _format_learning_plan(self, plan: Dict) -> str:
        """格式化学习计划为文本"""
        text_parts = []
        
        text_parts.append(f"学习计划：{plan.get('title', '未命名计划')}")
        
        if plan.get('description'):
            text_parts.append(f"描述：{plan['description']}")
        
        if plan.get('objectives'):
            text_parts.append("学习目标：")
            for obj in plan['objectives']:
                text_parts.append(f"- {obj}")
        
        if plan.get('content'):
            text_parts.append("学习内容：")
            content = plan['content']
            if isinstance(content, dict):
                for key, value in content.items():
                    text_parts.append(f"{key}: {value}")
            else:
                text_parts.append(str(content))
        
        return "\n".join(text_parts)
    
    def _format_student_profile(self, profile: Dict) -> str:
        """格式化学生档案为文本"""
        text_parts = []
        
        text_parts.append(f"学生姓名：{profile.get('name', '未知')}")
        text_parts.append(f"年龄：{profile.get('age', '未知')}")
        text_parts.append(f"年级：{profile.get('grade', '未知')}")
        
        if profile.get('interests'):
            text_parts.append(f"兴趣爱好：{', '.join(profile['interests'])}")
        
        if profile.get('learning_goals'):
            text_parts.append(f"学习目标：{profile['learning_goals']}")
        
        if profile.get('learning_style'):
            text_parts.append(f"学习风格：{profile['learning_style']}")
        
        if profile.get('background'):
            text_parts.append(f"背景信息：{profile['background']}")
        
        return "\n".join(text_parts)
    
    def clear_collection(self, collection_name: str):
        """清空指定集合（仅用于测试）"""
        try:
            collection = self.chroma_client.get_collection(collection_name)
            # 获取所有文档ID并删除
            results = collection.get()
            if results['ids']:
                collection.delete(ids=results['ids'])
        except:
            pass 