from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from backend.models import User, Student, Teacher, Subject, Mark
from backend.schemas import UserCreate, StudentCreate, TeacherCreate, SubjectCreate, MarkCreate, MarkUpdate
from backend.auth import get_password_hash

# --- Users ---

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# --- Admin Operations ---

def admin_create_teacher(db: Session, teacher: TeacherCreate):
    # 1. Create User
    db_user = User(
        name=teacher.name, 
        email=teacher.email, 
        password_hash=get_password_hash(teacher.password), 
        role="teacher"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # 2. Create Teacher mapping
    db_teacher = Teacher(user_id=db_user.id)
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

def admin_create_student(db: Session, student: StudentCreate):
    # 1. Create User
    db_user = User(
        name=student.name, 
        email=student.email, 
        password_hash=get_password_hash(student.password), 
        role="student"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # 2. Create Student mapping
    db_student = Student(user_id=db_user.id, class_name=student.class_name, roll_number=student.roll_number)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def admin_get_all_students(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Student).offset(skip).limit(limit).all()

def admin_get_all_teachers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Teacher).offset(skip).limit(limit).all()

def admin_create_subject(db: Session, subject: SubjectCreate):
    db_subject = Subject(name=subject.name)
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

def admin_assign_subject_to_teacher(db: Session, subject_id: int, teacher_id: int):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if subject:
        subject.teacher_id = teacher_id
        db.commit()
        db.refresh(subject)
    return subject

def admin_get_all_subjects(db: Session):
    return db.query(Subject).all()

def admin_get_all_marks(db: Session):
    return db.query(Mark).all()

# --- Teacher Operations ---

def teacher_get_my_subjects(db: Session, teacher_user_id: int):
    teacher = db.query(Teacher).filter(Teacher.user_id == teacher_user_id).first()
    if not teacher: return []
    return db.query(Subject).filter(Subject.teacher_id == teacher.id).all()

def teacher_get_my_students(db: Session, teacher_user_id: int):
    # Teachers can view students who have marks in their subjects, 
    # OR potentially all students if they need to add marks. For now, return all students 
    # so they can grade them in their assigned classes.
    return db.query(Student).all()

def teacher_create_mark(db: Session, mark: MarkCreate, teacher_user_id: int):
    teacher = db.query(Teacher).filter(Teacher.user_id == teacher_user_id).first()
    if not teacher: raise ValueError("Teacher profile not found")
    
    # Verify the teacher owns this subject
    subject = db.query(Subject).filter(Subject.id == mark.subject_id, Subject.teacher_id == teacher.id).first()
    if not subject:
        raise ValueError("You are not assigned to teach this subject.")
        
    db_mark = Mark(**mark.model_dump())
    db.add(db_mark)
    db.commit()
    db.refresh(db_mark)
    return db_mark

def teacher_update_mark(db: Session, mark_id: int, mark_update: MarkUpdate, teacher_user_id: int):
    teacher = db.query(Teacher).filter(Teacher.user_id == teacher_user_id).first()
    
    db_mark = db.query(Mark).filter(Mark.id == mark_id).first()
    if not db_mark: return None
    
    # Verify ownership
    subject = db.query(Subject).filter(Subject.id == db_mark.subject_id, Subject.teacher_id == teacher.id).first()
    if not subject:
        raise ValueError("You are not assigned to teach this subject.")
        
    db_mark.marks = mark_update.marks
    db.commit()
    db.refresh(db_mark)
    return db_mark

# --- Student Operations ---

def student_get_my_profile(db: Session, student_user_id: int):
    return db.query(Student).filter(Student.user_id == student_user_id).first()

def student_get_my_marks(db: Session, student_user_id: int):
    student = student_get_my_profile(db, student_user_id)
    if not student: return []
    return db.query(Mark).filter(Mark.student_id == student.id).all()


# --- Analytics (Admin) ---

def get_leaderboard(db: Session):
    results = db.query(
        Student.id,
        User.name,
        func.avg(Mark.marks).label('average_marks')
    ).join(User, Student.user_id == User.id)\
     .join(Mark, Student.id == Mark.student_id)\
     .group_by(Student.id, User.name)\
     .order_by(desc('average_marks'))\
     .all()
    
    return [
        {"student_id": r[0], "student_name": r[1], "average_marks": round(float(r[2]), 2)}
        for r in results
    ]

def get_subject_averages(db: Session):
    results = db.query(
        Subject.name,
        func.avg(Mark.marks).label('average_marks')
    ).join(Mark, Subject.id == Mark.subject_id)\
     .group_by(Subject.name)\
     .all()
     
    return [{"subject_name": r[0], "average_marks": round(float(r[1]), 2)} for r in results]


# --- Analytics (Teacher) ---

def teacher_get_subject_averages(db: Session, teacher_user_id: int):
    teacher = db.query(Teacher).filter(Teacher.user_id == teacher_user_id).first()
    if not teacher: return []
    
    results = db.query(
        Subject.name,
        func.avg(Mark.marks).label('average_marks')
    ).join(Mark, Subject.id == Mark.subject_id)\
     .filter(Subject.teacher_id == teacher.id)\
     .group_by(Subject.name)\
     .all()
     
    return [{"subject_name": r[0], "average_marks": round(float(r[1]), 2)} for r in results]

# --- Analytics (Student) ---
def student_get_my_stats(db: Session, student_user_id: int):
    student = student_get_my_profile(db, student_user_id)
    if not student: return None
    
    # Calc own average
    avg_result = db.query(func.avg(Mark.marks)).filter(Mark.student_id == student.id).scalar()
    own_avg = round(float(avg_result), 2) if avg_result else 0.0
    
    # Calc rank (simple in-memory sort)
    lb = get_leaderboard(db)
    rank = 0
    percentile = 0.0
    for i, entry in enumerate(lb):
        if entry["student_id"] == student.id:
            rank = i + 1
            break
            
    if len(lb) > 1 and rank > 0:
        percentile = ((len(lb) - rank) / (len(lb) - 1)) * 100
        
    return {
        "student_id": student.id,
        "average_marks": own_avg,
        "rank": rank,
        "percentile": round(percentile, 2)
    }

