"""
学生管理相关的API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from ...core.database import get_db
from ...models import Student, LearningPlan
from ...schemas.student import StudentCreate, StudentUpdate, StudentResponse, StudentWithPlans
from ...services.rag_service import RAGService

router = APIRouter()


@router.post("", response_model=StudentResponse)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """创建新学生"""
    # 创建学生对象
    db_student = Student(
        id=str(uuid.uuid4()),
        **student.dict()
    )
    
    # 保存到数据库
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    
    # 将学生档案存储到向量数据库
    try:
        rag_service = RAGService()
        rag_service.store_student_profile(
            db_student.id,
            db_student.to_dict()
        )
    except Exception as e:
        print(f"存储学生档案到向量数据库失败: {e}")
    
    return db_student


@router.get("", response_model=List[StudentResponse])
def read_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取学生列表"""
    students = db.query(Student).offset(skip).limit(limit).all()
    return students


@router.get("/{student_id}", response_model=StudentWithPlans)
def read_student(student_id: str, db: Session = Depends(get_db)):
    """获取单个学生信息"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # 获取学生的学习计划
    plans = db.query(LearningPlan).filter(LearningPlan.student_id == student_id).all()
    
    return StudentWithPlans(
        **student.__dict__,
        learning_plans=plans
    )


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: str,
    student_update: StudentUpdate,
    db: Session = Depends(get_db)
):
    """更新学生信息"""
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # 更新字段
    update_data = student_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_student, field, value)
    
    # 保存到数据库
    db.commit()
    db.refresh(db_student)
    
    # 更新向量数据库中的学生档案
    try:
        rag_service = RAGService()
        rag_service.store_student_profile(
            db_student.id,
            db_student.to_dict()
        )
    except Exception as e:
        print(f"更新学生档案到向量数据库失败: {e}")
    
    return db_student


@router.delete("/{student_id}")
def delete_student(student_id: str, db: Session = Depends(get_db)):
    """删除学生"""
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(db_student)
    db.commit()
    
    return {"message": "Student deleted successfully"}


@router.get("/{student_id}/similar", response_model=List[dict])
def find_similar_students(
    student_id: str,
    k: int = 3,
    db: Session = Depends(get_db)
):
    """查找相似的学生"""
    # 确认学生存在
    student = db.query(Student).filter(Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # 使用RAG服务查找相似学生
    try:
        rag_service = RAGService()
        similar_students = rag_service.find_similar_students(student_id, k)
        
        # 获取相似学生的详细信息
        result = []
        for similar in similar_students:
            student_data = db.query(Student).filter(
                Student.id == similar['id']
            ).first()
            if student_data:
                result.append({
                    "student": student_data.to_dict(),
                    "similarity": similar.get('similarity', 0)
                })
        
        return result
    except Exception as e:
        print(f"查找相似学生失败: {e}")
        return []


@router.get("/{student_id}/learning-plans", response_model=List[dict])
def get_student_learning_plans(
    student_id: str,
    db: Session = Depends(get_db)
):
    """获取学生的学习计划"""
    # 确认学生存在
    student = db.query(Student).filter(Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # 获取学习计划
    plans = db.query(LearningPlan).filter(
        LearningPlan.student_id == student_id
    ).order_by(LearningPlan.created_at.desc()).all()
    
    # 转换为字典列表
    return [plan.to_dict() for plan in plans] 