from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String(50), nullable=False) # admin, teacher, student

    # Relationships mapped to derived tables
    student_profile = relationship("Student", back_populates="user", uselist=False, cascade="all, delete")
    teacher_profile = relationship("Teacher", back_populates="user", uselist=False, cascade="all, delete")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    class_name = Column(String(100), nullable=False, name="class_name")
    roll_number = Column(String(50), unique=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="student_profile")
    marks = relationship("Mark", back_populates="student", cascade="all, delete")


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="teacher_profile")
    subjects = relationship("Subject", back_populates="teacher", cascade="all, delete-orphan")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    teacher = relationship("Teacher", back_populates="subjects")
    marks = relationship("Mark", back_populates="subject", cascade="all, delete")


class Mark(Base):
    __tablename__ = "marks"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    marks = Column(Numeric(5, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Ensure a student can only have 1 marks entry per subject
    __table_args__ = (UniqueConstraint('student_id', 'subject_id', name='uq_student_subject_marks'),)

    # Relationships
    student = relationship("Student", back_populates="marks")
    subject = relationship("Subject", back_populates="marks")
