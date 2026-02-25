# Student Performance & Analytics System

A production-ready full-stack application built using FastAPI for the backend and Flask for the frontend, with a PostgreSQL database.

## System Requirements
- Python 3.9+ 
- PostgreSQL

## Setup Instructions

### 1. Database Setup
1. Create a PostgreSQL database (e.g., named `student_performance`)
2. Use the provided Python script to completely rebuild and seed the database with mock data for all roles:
   ```bash
   python seed_db.py
   ```
   *Pre-seeded Accounts:*
   * Admin: `admin@school.com` / `admin123`
   * Teacher 1: `teacher1@school.com` / `teacher123`
   * Student 1: `student1@school.com` / `student123`

### 2. Install Dependencies
Create a virtual environment and install the required packages:
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Environment Variables
Create `.env` file in the project root with the following (update with your DB credentials):
```env
# Backend Settings
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/student_performance
SECRET_KEY=yoursecretkey_generate_something_long_and_random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Frontend Settings
FLASK_SECRET_KEY=your_flask_secret_key
API_BASE_URL=http://localhost:8000
```

### 4. Running the Application

**Run Backend (FastAPI)**
```bash
# In the project root
uvicorn backend.main:app --reload
```
The backend API and swagger docs will be available at: http://localhost:8000/docs

**Run Frontend (Flask)**
Open another terminal:
```bash
# activate venv if needed
python frontend/app.py
```
Access the application interface at: http://localhost:5000

## Features
- JWT based Role Authorization (admin, teacher, student)
- Student CRUD
- Subject Management
- Marks Management
- Analytics & Leaderboards with Chart.js
