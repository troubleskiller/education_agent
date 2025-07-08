"""
RAG（检索增强生成）服务
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Any
import json
import uuid

from ..core.config import settings


class RAGService:
    """RAG服务类，使用本地ChromaDB"""
    
    def __init__(self):
        """初始化RAG服务"""
        # 初始化本地ChromaDB客户端
        self.client = chromadb.PersistentClient(
            path=settings.vector_db_path,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 初始化嵌入模型
        if settings.embeddings_provider == "openai":
            # 使用OpenAI的嵌入模型
            self.embeddings = OpenAIEmbeddings(
                api_key=settings.openai_api_key,
                model="text-embedding-3-small"  # 使用较小的模型以降低成本
            )
        else:
            # 使用本地嵌入模型（免费）
            self.embeddings = HuggingFaceEmbeddings(
                model_name=settings.local_embeddings_model,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        
        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        )
        
        # 创建或获取集合
        self._init_collections()
    
    def _init_collections(self):
        """初始化向量数据库集合"""
        # 学习计划集合
        self.learning_plans_collection = self.client.get_or_create_collection(
            name="learning_plans",
            metadata={"description": "存储学生的个性化学习计划"}
        )
        
        # 教学材料集合
        self.teaching_materials_collection = self.client.get_or_create_collection(
            name="teaching_materials",
            metadata={"description": "存储教学材料和知识点"}
        )
        
        # 学生档案集合
        self.student_profiles_collection = self.client.get_or_create_collection(
            name="student_profiles",
            metadata={"description": "存储学生档案和学习历史"}
        )
    
    def store_learning_plan(self, student_id: str, plan_id: str, plan_data: Dict[str, Any]):
        """存储学习计划到向量数据库"""
        # 准备文档内容
        doc_content = f"""
学生ID: {student_id}
计划标题: {plan_data.get('title', '')}
计划描述: {plan_data.get('description', '')}
学习目标: {', '.join(plan_data.get('objectives', []))}
预计时长: {plan_data.get('estimated_days', 0)}天
难度级别: {plan_data.get('difficulty_level', 0)}/5

详细内容:
{json.dumps(plan_data.get('content', {}), ensure_ascii=False, indent=2)}
"""
        
        # 获取嵌入向量
        embedding = self.embeddings.embed_query(doc_content)
        
        # 存储到ChromaDB
        self.learning_plans_collection.add(
            ids=[plan_id],
            embeddings=[embedding],
            documents=[doc_content],
            metadatas=[{
                "student_id": student_id,
                "plan_id": plan_id,
                "title": plan_data.get('title', ''),
                "created_at": plan_data.get('created_at', ''),
                "type": "learning_plan"
            }]
        )
    
    def search_learning_plans(self, query: str, student_id: str = None, k: int = 5) -> List[Dict]:
        """搜索学习计划"""
        # 构建查询条件
        where_clause = {"type": "learning_plan"}
        if student_id:
            where_clause["student_id"] = student_id
        
        # 获取查询的嵌入向量
        query_embedding = self.embeddings.embed_query(query)
        
        # 执行搜索
        results = self.learning_plans_collection.query(
            query_embeddings=[query_embedding],
            where=where_clause,
            n_results=k
        )
        
        # 格式化返回结果
        formatted_results = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
        
        return formatted_results
    
    def store_teaching_material(self, material_id: str, content: str, metadata: Dict[str, Any]):
        """存储教学材料"""
        # 分割文本
        chunks = self.text_splitter.split_text(content)
        
        # 为每个块生成ID和嵌入
        chunk_ids = []
        chunk_embeddings = []
        chunk_metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{material_id}_chunk_{i}"
            chunk_ids.append(chunk_id)
            
            # 获取嵌入向量
            embedding = self.embeddings.embed_query(chunk)
            chunk_embeddings.append(embedding)
            
            # 准备元数据
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "material_id": material_id,
                "chunk_index": i,
                "type": "teaching_material"
            })
            chunk_metadatas.append(chunk_metadata)
        
        # 批量存储到ChromaDB
        if chunk_ids:
            self.teaching_materials_collection.add(
                ids=chunk_ids,
                embeddings=chunk_embeddings,
                documents=chunks,
                metadatas=chunk_metadatas
            )
    
    def search_teaching_materials(self, query: str, subject: str = None, k: int = 5) -> List[Dict]:
        """搜索教学材料"""
        # 构建查询条件
        where_clause = {"type": "teaching_material"}
        if subject:
            where_clause["subject"] = subject
        
        # 获取查询的嵌入向量
        query_embedding = self.embeddings.embed_query(query)
        
        # 执行搜索
        results = self.teaching_materials_collection.query(
            query_embeddings=[query_embedding],
            where=where_clause,
            n_results=k
        )
        
        # 格式化返回结果
        formatted_results = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
        
        return formatted_results
    
    def store_student_profile(self, student_id: str, profile_data: Dict[str, Any]):
        """存储学生档案到向量数据库"""
        # 准备文档内容
        doc_content = f"""
学生姓名: {profile_data.get('name', '')}
年龄: {profile_data.get('age', '')}
年级: {profile_data.get('grade', '')}
学习风格: {profile_data.get('learning_style', '')}
兴趣爱好: {', '.join(profile_data.get('interests', []))}
学习目标: {profile_data.get('learning_goals', '')}
"""
        
        # 获取嵌入向量
        embedding = self.embeddings.embed_query(doc_content)
        
        # 存储到ChromaDB
        self.student_profiles_collection.upsert(
            ids=[student_id],
            embeddings=[embedding],
            documents=[doc_content],
            metadatas=[{
                "student_id": student_id,
                "name": profile_data.get('name', ''),
                "type": "student_profile"
            }]
        )
    
    def find_similar_students(self, student_id: str, k: int = 3) -> List[Dict]:
        """查找相似的学生档案"""
        # 先获取当前学生的档案
        current_student = self.student_profiles_collection.get(
            ids=[student_id]
        )
        
        if not current_student['ids']:
            return []
        
        # 使用当前学生的档案内容进行相似度搜索
        current_doc = current_student['documents'][0]
        query_embedding = self.embeddings.embed_query(current_doc)
        
        # 搜索相似学生（排除自己）
        results = self.student_profiles_collection.query(
            query_embeddings=[query_embedding],
            where={"type": "student_profile"},
            n_results=k + 1  # 多查一个，因为要排除自己
        )
        
        # 格式化结果并排除自己
        formatted_results = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                if results['ids'][0][i] != student_id:
                    formatted_results.append({
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'similarity': 1 - results['distances'][0][i] if 'distances' in results else None
                    })
        
        return formatted_results[:k]
    
    def clear_collection(self, collection_name: str):
        """清空指定的集合（用于测试或重置）"""
        try:
            self.client.delete_collection(collection_name)
            # 重新初始化集合
            self._init_collections()
        except Exception as e:
            print(f"清空集合 {collection_name} 失败: {e}") 