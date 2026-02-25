import sys
import random
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine
from backend.models import User, Student, Teacher, Subject, Mark, Base
from backend.auth import get_password_hash

def reset_db():
    print("Dropping tables...")
    Base.metadata.drop_all(bind=engine)
    print("Recreating tables...")
    Base.metadata.create_all(bind=engine)

def seed_db():
    db = SessionLocal()
    
    print("Seeding database (RBAC Phase 2 + Analytics Polish)...")
    
    # 1. Create ADMIN
    admin = User(name="System Admin", email="admin@school.com", password_hash=get_password_hash("admin123"), role="admin")
    db.add(admin)
    db.commit()
    
    # 2. Create TEACHERS (5 teachers)
    teachers_data = [
        {"name": "Mr. Smith", "email": "teacher1@school.com"},
        {"name": "Ms. Davis", "email": "teacher2@school.com"},
        {"name": "Dr. House", "email": "teacher3@school.com"},
        {"name": "Mrs. Robinson", "email": "teacher4@school.com"},
        {"name": "Prof. X", "email": "teacher5@school.com"}
    ]
    
    db_teachers = []
    db_teacher_users = []
    
    for t_data in teachers_data:
        user = User(name=t_data["name"], email=t_data["email"], password_hash=get_password_hash("teacher123"), role="teacher")
        db.add(user)
        db_teacher_users.append(user)
        
    db.commit() # commit users to get IDs
    
    for user in db_teacher_users:
        teacher = Teacher(user_id=user.id)
        db.add(teacher)
        db_teachers.append(teacher)
        
    db.commit()

    # 3. Create STUDENTS (15 students)
    student_names = [
        "Alice Johnson", "Bob Williams", "Charlie Brown", "Diana Prince", "Evan Wright",
        "Fiona Gallagher", "George Miller", "Hannah Abbott", "Ian Malcolm", "Jane Doe",
        "Kevin McCallister", "Laura Palmer", "Michael Scott", "Nancy Wheeler", "Oliver Twist"
    ]
    
    db_students = []
    db_student_users = []
    
    for i, name in enumerate(student_names):
        email = f"student{i+1}@school.com"
        user = User(name=name, email=email, password_hash=get_password_hash("student123"), role="student")
        db.add(user)
        db_student_users.append(user)
        
    db.commit()
    
    for i, user in enumerate(db_student_users):
        class_name = f"Grade {10 if i < 8 else 11}"
        roll = f"{10 if i < 8 else 11}{'A' if i % 2 == 0 else 'B'}-{i+1:02d}"
        student = Student(user_id=user.id, class_name=class_name, roll_number=roll)
        db.add(student)
        db_students.append(student)
        
    db.commit()
    
    # 4. Create SUBJECTS and Assign Teachers (10 subjects)
    subjects_data = [
        ("Mathematics", db_teachers[0].id),
        ("Physics", db_teachers[0].id),
        ("Literature", db_teachers[1].id),
        ("History", db_teachers[1].id),
        ("Biology", db_teachers[2].id),
        ("Chemistry", db_teachers[2].id),
        ("Art", db_teachers[3].id),
        ("Music", db_teachers[3].id),
        ("Computer Science", db_teachers[4].id),
        ("Physical Education", db_teachers[4].id)
    ]
    
    db_subjects = []
    for name, t_id in subjects_data:
        sub = Subject(name=name, teacher_id=t_id)
        db.add(sub)
        db_subjects.append(sub)
        
    db.commit()
    
    # 5. Add Marks (Give every student 6-8 subjects with random marks)
    marks = []
    for student in db_students:
        # Pick a random subset of subjects for this student
        student_subjects = random.sample(db_subjects, k=random.randint(6, 8))
        
        # Determine if this student is a high achiever, average, or struggling
        performance_profile = random.choice(["high", "avg", "struggling"])
        
        for subject in student_subjects:
            if performance_profile == "high":
                score = round(random.uniform(80.0, 99.5), 2)
            elif performance_profile == "avg":
                score = round(random.uniform(55.0, 85.0), 2)
            else:
                score = round(random.uniform(30.0, 65.0), 2)
                
            marks.append(Mark(student_id=student.id, subject_id=subject.id, marks=score))
            
    db.add_all(marks)
    db.commit()
    
    print(f"Database seeding completed: 1 Admin, {len(db_teachers)} Teachers, {len(db_students)} Students, {len(db_subjects)} Subjects, {len(marks)} Marks!")
    db.close()

if __name__ == "__main__":
    reset_db()
    seed_db()
