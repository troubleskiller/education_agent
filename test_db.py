"""
测试数据库初始化
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("测试数据库连接...")
    from src.core.database import Base, engine
    from src.models import Student, Conversation, Message, LearningPlan, LearningProgress
    
    print("✓ 成功导入所有模型")
    
    # 创建所有表
    print("\n创建数据库表...")
    Base.metadata.create_all(bind=engine)
    
    print("✓ 数据库表创建成功")
    
    # 列出所有表
    print("\n已创建的表：")
    for table in Base.metadata.tables.keys():
        print(f"  - {table}")
    
    print("\n数据库初始化测试成功！")
    
except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc() 