from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend import crud, schemas, models
from backend.database import get_db
from backend.auth import get_current_teacher

router = APIRouter(
    prefix="/api/teacher",
    tags=["teacher"],
    dependencies=[Depends(get_current_teacher)]
)

@router.get("/subjects/", response_model=List[schemas.Subject])
def get_my_subjects(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_teacher)):
    return crud.teacher_get_my_subjects(db, current_user.id)

@router.get("/students/", response_model=List[schemas.Student])
def get_my_students(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_teacher)):
    return crud.teacher_get_my_students(db, current_user.id)

@router.post("/marks/", response_model=schemas.Mark)
def add_mark(mark: schemas.MarkCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_teacher)):
    try:
        return crud.teacher_create_mark(db, mark, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.put("/marks/{mark_id}", response_model=schemas.Mark)
def update_mark(mark_id: int, mark: schemas.MarkUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_teacher)):
    try:
        result = crud.teacher_update_mark(db, mark_id, mark, current_user.id)
        if not result:
            raise HTTPException(status_code=404, detail="Mark not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.delete("/marks/{mark_id}")
def delete_mark(mark_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_teacher)):
    teacher = db.query(models.Teacher).filter(models.Teacher.user_id == current_user.id).first()
    db_mark = db.query(models.Mark).filter(models.Mark.id == mark_id).first()
    
    if db_mark:
        subject = db.query(models.Subject).filter(models.Subject.id == db_mark.subject_id, models.Subject.teacher_id == teacher.id).first()
        if not subject:
            raise HTTPException(status_code=403, detail="Not authorized to delete this record")
        db.delete(db_mark)
        db.commit()
    return {"message": "Success"}
