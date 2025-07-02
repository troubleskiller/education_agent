"""
数据库初始化脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.database import Base, engine
from src.models import Student, Conversation, Message, LearningPlan, LearningProgress


def init_database():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    print("数据库初始化完成！")
    print("已创建以下表：")
    print("- students: 学生信息表")
    print("- conversations: 对话记录表")
    print("- messages: 消息记录表")
    print("- learning_plans: 学习计划表")
    print("- learning_progress: 学习进度表")


if __name__ == "__main__":
    init_database() 