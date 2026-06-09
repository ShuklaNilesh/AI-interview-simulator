import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship
from backend.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    target_role = Column(String, default="Software Engineer")
    experience_level = Column(String, default="Intermediate")
    streak_count = Column(Integer, default=0)
    last_active_date = Column(DateTime, default=datetime.datetime.utcnow)
    is_admin = Column(Boolean, default=False)
    
    sessions = relationship("InterviewSession", back_populates="user", cascade="all, delete-orphan")
    resumes = relationship("ResumeAnalysis", back_populates="user", cascade="all, delete-orphan")
    career_chats = relationship("CareerChat", back_populates="user", cascade="all, delete-orphan")


class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String, nullable=False)
    difficulty = Column(String, nullable=False) # Beginner, Intermediate, Advanced
    type = Column(String, nullable=False) # HR, Technical, Behavioral, Coding, Mixed
    mode = Column(String, nullable=False) # Voice, Text, Text-to-Speech
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="ongoing") # ongoing, completed
    
    # Summary Scores
    overall_score = Column(Float, nullable=True)
    technical_score = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    fluency_score = Column(Float, nullable=True)
    hr_score = Column(Float, nullable=True)
    
    detailed_feedback = Column(Text, nullable=True)
    learning_roadmap = Column(Text, nullable=True)
    
    user = relationship("User", back_populates="sessions")
    questions = relationship("InterviewQuestion", back_populates="session", cascade="all, delete-orphan")
    coding_submissions = relationship("CodingSubmission", back_populates="session", cascade="all, delete-orphan")


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("interview_sessions.id"))
    question_text = Column(Text, nullable=False)
    user_answer = Column(Text, nullable=True)
    feedback_text = Column(Text, nullable=True)
    suggestion = Column(Text, nullable=True)
    category = Column(String, nullable=True) # Technical, HR, Behavioral
    
    # Individual scores
    technical_score = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    fluency_score = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    session = relationship("InterviewSession", back_populates="questions")


class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String, nullable=False)
    ats_score = Column(Integer, nullable=False)
    missing_keywords = Column(Text, nullable=True) # Comma separated or JSON string
    strengths = Column(Text, nullable=True)
    weaknesses = Column(Text, nullable=True)
    parsed_skills = Column(Text, nullable=True) # Comma separated
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="resumes")


class CodingSubmission(Base):
    __tablename__ = "coding_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("interview_sessions.id"))
    language = Column(String, nullable=False)
    code = Column(Text, nullable=False)
    complexity = Column(String, nullable=True) # Time & Space e.g. "O(N) Time, O(1) Space"
    test_cases_passed = Column(String, nullable=True) # e.g. "4/5"
    hints_used = Column(Integer, default=0)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    session = relationship("InterviewSession", back_populates="coding_submissions")


class CareerChat(Base):
    __tablename__ = "career_chats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String, default="user") # user, assistant
    message_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="career_chats")
