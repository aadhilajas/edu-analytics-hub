from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend import crud, schemas, models
from backend.database import get_db
from backend.auth import get_current_admin

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin)]
)

@router.post("/teachers/", response_model=schemas.Teacher)
def create_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=teacher.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.admin_create_teacher(db=db, teacher=teacher)

@router.post("/students/", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=student.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.admin_create_student(db=db, student=student)

@router.get("/students/", response_model=List[schemas.Student])
def read_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.admin_get_all_students(db, skip=skip, limit=limit)

@router.get("/teachers/", response_model=List[schemas.Teacher])
def read_teachers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.admin_get_all_teachers(db, skip=skip, limit=limit)

@router.post("/subjects/", response_model=schemas.Subject)
def create_subject(subject: schemas.SubjectCreate, db: Session = Depends(get_db)):
    db_subject = db.query(models.Subject).filter(models.Subject.name == subject.name).first()
    if db_subject:
        raise HTTPException(status_code=400, detail="Subject already exists")
    return crud.admin_create_subject(db=db, subject=subject)

@router.get("/subjects/", response_model=List[schemas.Subject])
def read_subjects(db: Session = Depends(get_db)):
    return crud.admin_get_all_subjects(db)

@router.put("/subjects/{subject_id}/assign", response_model=schemas.Subject)
def assign_subject_teacher(subject_id: int, assign: schemas.SubjectAssign, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == assign.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    subject = crud.admin_assign_subject_to_teacher(db, subject_id, assign.teacher_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject

@router.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if db_student:
        db.delete(db_student)
        db.commit()
    return {"message": "Success"}

@router.delete("/teachers/{teacher_id}")
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    db_teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if db_teacher:
        db.delete(db_teacher)
        db.commit()
    return {"message": "Success"}

@router.delete("/subjects/{subject_id}")
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    db_subject = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if db_subject:
        db.delete(db_subject)
        db.commit()
    return {"message": "Success"}
