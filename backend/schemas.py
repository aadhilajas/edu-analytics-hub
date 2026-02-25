from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# --- Token ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

# --- User ---
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    role: str = Field(..., description="admin, teacher, student")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class User(UserBase):
    id: int
    class Config:
        from_attributes = True

# --- Student ---
class StudentBase(BaseModel):
    class_name: str
    roll_number: str

class StudentCreate(StudentBase):
    name: str
    email: EmailStr
    password: str

class Student(StudentBase):
    id: int
    user_id: int
    user: UserBase
    class Config:
        from_attributes = True

# --- Teacher ---
class TeacherCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class Teacher(BaseModel):
    id: int
    user_id: int
    user: UserBase
    class Config:
        from_attributes = True

# --- Subject ---
class SubjectBase(BaseModel):
    name: str

class SubjectCreate(SubjectBase):
    pass

class SubjectAssign(BaseModel):
    teacher_id: int

class Subject(SubjectBase):
    id: int
    teacher_id: Optional[int]
    class Config:
        from_attributes = True

class SubjectWithTeacher(Subject):
    teacher: Optional[Teacher]

# --- Mark ---
class MarkBase(BaseModel):
    marks: float = Field(..., ge=0, le=100)

class MarkCreate(MarkBase):
    student_id: int
    subject_id: int

class MarkUpdate(MarkBase):
    pass

class Mark(MarkBase):
    id: int
    student_id: int
    subject_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class MarkDetail(Mark):
    student: Student
    subject: Subject
    class Config:
        from_attributes = True


# --- Analytics ---
class LeaderboardEntry(BaseModel):
    student_id: int
    student_name: str
    average_marks: float

class SubjectAverage(BaseModel):
    subject_name: str
    average_marks: float

class AtRiskStudent(BaseModel):
    student_id: int
    student_name: str
    class_name: str
    failing_subjects: List[str]

class RankInfo(BaseModel):
    student_id: int
    average_marks: float
    rank: int
    percentile: float
