from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from backend.database import engine, Base, get_db
from backend.routers import auth, interviews, resumes, coding, career
from backend.models import User, InterviewSession, InterviewQuestion, ResumeAnalysis
from backend.auth import get_current_admin
from backend.config import settings

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend services for InterviewAce AI – AI Interview Simulator & Career Coach",
    version="1.0.0"
)

# CORS Policy configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, lock this down to frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register endpoints routers
app.include_router(auth.router)
app.include_router(interviews.router)
app.include_router(resumes.router)
app.include_router(coding.router)
app.include_router(career.router)

@app.get("/")
def get_root_status():
    return {
        "status": "healthy",
        "service": "InterviewAce AI Backend Engine",
        "database": settings.DATABASE_URL.split(":///")[0]
    }

@app.get("/api/admin/analytics")
def get_admin_analytics(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Total aggregates
    total_users = db.query(User).count()
    total_interviews = db.query(InterviewSession).count()
    total_completed = db.query(InterviewSession).filter(InterviewSession.status == "completed").count()
    total_resumes = db.query(ResumeAnalysis).count()
    
    # Calculate average overall score
    avg_score_query = db.query(InterviewSession).filter(
        InterviewSession.status == "completed"
    ).all()
    avg_score = 0
    if avg_score_query:
        avg_score = sum(s.overall_score for s in avg_score_query if s.overall_score) / len(avg_score_query)
        
    # Interview type breakdown
    type_counts = {}
    for session in db.query(InterviewSession).all():
        type_counts[session.type] = type_counts.get(session.type, 0) + 1
        
    # Difficulty breakdown
    difficulty_counts = {}
    for session in db.query(InterviewSession).all():
        difficulty_counts[session.difficulty] = difficulty_counts.get(session.difficulty, 0) + 1
        
    return {
        "total_users": total_users,
        "total_interviews": total_interviews,
        "completed_interviews": total_completed,
        "total_resumes_analyzed": total_resumes,
        "average_score": round(avg_score, 1),
        "type_breakdown": type_counts,
        "difficulty_breakdown": difficulty_counts
    }

@app.get("/api/admin/users")
def get_admin_users(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()
    user_list = []
    for u in users:
        # Calculate stats for this user
        user_sessions = db.query(InterviewSession).filter(InterviewSession.user_id == u.id).all()
        completed = [s for s in user_sessions if s.status == "completed"]
        avg = 0
        if completed:
            avg = sum(s.overall_score for s in completed if s.overall_score) / len(completed)
            
        user_list.append({
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "target_role": u.target_role,
            "experience_level": u.experience_level,
            "streak_count": u.streak_count,
            "is_admin": u.is_admin,
            "last_active_date": u.last_active_date,
            "total_sessions": len(user_sessions),
            "average_score": round(avg, 1)
        })
    return user_list

@app.get("/api/admin/users/{user_id}/sessions")
def get_admin_user_sessions(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    sessions = db.query(InterviewSession).filter(InterviewSession.user_id == user_id).all()
    return sessions

