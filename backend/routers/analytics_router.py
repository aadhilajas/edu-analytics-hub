from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict

from backend import crud, schemas, models
from backend.database import get_db
from backend.auth import get_current_user

router = APIRouter(
    prefix="/api/analytics",
    tags=["analytics"]
)

# Shared but isolated logic router

@router.get("/admin/leaderboard", response_model=List[schemas.LeaderboardEntry])
def get_admin_leaderboard(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin": raise HTTPException(status_code=403, detail="Forbidden")
    return crud.get_leaderboard(db)

@router.get("/admin/subjects", response_model=List[schemas.SubjectAverage])
def get_admin_subjects(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin": raise HTTPException(status_code=403, detail="Forbidden")
    return crud.get_subject_averages(db)

@router.get("/teacher/subjects", response_model=List[schemas.SubjectAverage])
def get_teacher_subjects(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "teacher": raise HTTPException(status_code=403, detail="Forbidden")
    return crud.teacher_get_subject_averages(db, current_user.id)

@router.get("/student/stats", response_model=schemas.RankInfo)
def get_student_stats(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "student": raise HTTPException(status_code=403, detail="Forbidden")
    stats = crud.student_get_my_stats(db, current_user.id)
    if not stats: raise HTTPException(status_code=404, detail="Not found")
    return stats
