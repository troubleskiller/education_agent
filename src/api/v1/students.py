"""
学生API路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models import Student
from ...schemas.student import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentListResponse
)
from ...services.rag_service import RAGService

router = APIRouter(prefix="/students", tags=["students"])


@router.post("/", response_model=StudentResponse)
async def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    """创建新学生档案"""
    # 创建学生记录
    db_student = Student(
        name=student.name,
        age=student.age,
        grade=student.grade,
        interests=student.interests,
        background=student.background,
        learning_goals=student.learning_goals,
        learning_style=student.learning_style
    )
    
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    
    # 更新RAG中的学生档案
    rag_service = RAGService()
    rag_service.update_student_profile_embedding(
        db_student.id,
        db_student.to_dict()
    )
    
    return db_student


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: str,
    db: Session = Depends(get_db)
):
    """获取学生信息"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    return student


@router.get("/", response_model=StudentListResponse)
async def list_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取学生列表"""
    query = db.query(Student)
    total = query.count()
    students = query.offset(skip).limit(limit).all()
    
    return StudentListResponse(
        students=students,
        total=total
    )


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: str,
    student_update: StudentUpdate,
    db: Session = Depends(get_db)
):
    """更新学生信息"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    # 更新字段
    update_data = student_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)
    
    db.commit()
    db.refresh(student)
    
    # 更新RAG中的学生档案
    rag_service = RAGService()
    rag_service.update_student_profile_embedding(
        student.id,
        student.to_dict()
    )
    
    return student


@router.delete("/{student_id}")
async def delete_student(
    student_id: str,
    db: Session = Depends(get_db)
):
    """删除学生档案"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    db.delete(student)
    db.commit()
    
    return {"message": "学生档案已删除"}


@router.get("/{student_id}/similar", response_model=List[dict])
async def find_similar_students(
    student_id: str,
    k: int = Query(3, ge=1, le=10),
    db: Session = Depends(get_db)
):
    """查找相似的学生"""
    # 验证学生存在
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    # 查找相似学生
    rag_service = RAGService()
    similar_students = rag_service.find_similar_students(student_id, k)
    
    return similar_students 