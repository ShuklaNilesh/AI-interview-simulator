from backend.database import SessionLocal, Base, engine
from backend.models import User, InterviewSession, InterviewQuestion, ResumeAnalysis
from backend.auth import get_password_hash
import datetime

# Create schemas
Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    # 1. Create candidate user
    candidate_email = "candidate@example.com"
    candidate = db.query(User).filter(User.email == candidate_email).first()
    if not candidate:
        candidate = User(
            email=candidate_email,
            hashed_password=get_password_hash("candidate123"),
            full_name="Alex Mercer",
            target_role="Full Stack Developer",
            experience_level="Intermediate",
            streak_count=3,
            last_active_date=datetime.datetime.utcnow() - datetime.timedelta(hours=4)
        )
        db.add(candidate)
        db.flush() # get candidate.id
        
        # Add some mock interviews for candidate
        session1 = InterviewSession(
            id="mock-session-1",
            user_id=candidate.id,
            role="Full Stack Developer",
            difficulty="Intermediate",
            type="Technical",
            mode="text",
            status="completed",
            overall_score=78.0,
            technical_score=80.0,
            communication_score=75.0,
            confidence_score=70.0,
            fluency_score=85.0,
            hr_score=80.0,
            detailed_feedback="### Overall Feedback\nAlex demonstrated strong fundamentals in React state hooks and API architectures. Expresses code ideas clearly but should improve on database scaling explanations.\n\n### Strengths\n- React hooks and component rendering.\n- Clear, concise messaging style.\n\n### Areas to Improve\n- Explain horizontal scaling vs vertical scaling with specific examples.",
            learning_roadmap="### 1. Database Indexing & Scale\n- Study B-Trees and execution planning.\n- Practice standard design bottlenecks.\n\n### 2. Mock Practice\n- Practice system design questions regarding caching."
        )
        db.add(session1)
        
        q1 = InterviewQuestion(
            session_id="mock-session-1",
            question_text="How does React Virtual DOM optimize UI rendering?",
            user_answer="It uses a diffing algorithm to compare trees and only re-renders modified components in the actual DOM.",
            feedback_text="Excellent explanation of tree comparison and paint optimization.",
            suggestion="Mention reconciliation and key attributes specifically for a more advanced answer.",
            category="Technical",
            technical_score=85.0,
            communication_score=80.0,
            confidence_score=80.0,
            fluency_score=85.0
        )
        db.add(q1)

        resume1 = ResumeAnalysis(
            user_id=candidate.id,
            filename="Alex_Mercer_CV.pdf",
            ats_score=75,
            missing_keywords="Docker, Kubernetes, Redis, CI/CD",
            strengths="Clear experience in React, Node, Python, and relational database schema design.",
            weaknesses="Lacks cloud deployment orchestration context and automated test suite mentions.",
            parsed_skills="React, Node.js, Python, PostgreSQL, REST APIs, Git"
        )
        db.add(resume1)

    # 2. Create admin user
    admin_email = "admin@interviewace.ai"
    admin = db.query(User).filter(User.email == admin_email).first()
    if not admin:
        admin = User(
            email=admin_email,
            hashed_password=get_password_hash("admin123"),
            full_name="Principal System Admin",
            target_role="System Administrator",
            experience_level="Advanced",
            streak_count=1,
            is_admin=True,
            last_active_date=datetime.datetime.utcnow()
        )
        db.add(admin)

    db.commit()
    print("Database seeded successfully with default users:")
    print("Candidate: candidate@example.com / candidate123")
    print("Admin: admin@interviewace.ai / admin123")
except Exception as e:
    db.rollback()
    print(f"Error seeding database: {e}")
finally:
    db.close()
