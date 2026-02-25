from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend import crud, schemas, models
from backend.database import get_db
from backend.auth import get_current_student

router = APIRouter(
    prefix="/api/student",
    tags=["student"],
    dependencies=[Depends(get_current_student)]
)

@router.get("/profile", response_model=schemas.Student)
def get_profile(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_student)):
    profile = crud.student_get_my_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return profile

@router.get("/marks", response_model=List[schemas.MarkDetail])
def get_my_marks(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_student)):
    return crud.student_get_my_marks(db, current_user.id)
