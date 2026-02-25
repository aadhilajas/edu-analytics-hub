from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import auth_router, admin_router, teacher_router, student_router, analytics_router
from backend.database import engine
from backend import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Student Performance & Analytics System (RBAC)")

# CORS settings for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router.router)
app.include_router(admin_router.router)
app.include_router(teacher_router.router)
app.include_router(student_router.router)
app.include_router(analytics_router.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Student Performance & Analytics RBAC API! Navigate to /docs for Swagger."}
