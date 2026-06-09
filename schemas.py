from pydantic import BaseModel, EmailStr
from typing import List, Optional, Any
from datetime import datetime

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    target_role: Optional[str] = "Software Engineer"
    experience_level: Optional[str] = "Intermediate"

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    streak_count: int
    last_active_date: datetime
    is_admin: bool

    class Config:
        from_attributes = True

# --- Question Schemas ---
class InterviewQuestionBase(BaseModel):
    question_text: str

class InterviewQuestionResponse(InterviewQuestionBase):
    id: int
    session_id: str
    user_answer: Optional[str] = None
    feedback_text: Optional[str] = None
    suggestion: Optional[str] = None
    category: Optional[str] = None
    technical_score: Optional[float] = None
    communication_score: Optional[float] = None
    confidence_score: Optional[float] = None
    fluency_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AnswerSubmit(BaseModel):
    answer: str

# --- Coding Submission Schemas ---
class CodingSubmissionCreate(BaseModel):
    language: str
    code: str

class CodingSubmissionResponse(CodingSubmissionCreate):
    id: int
    session_id: str
    complexity: Optional[str] = None
    test_cases_passed: Optional[str] = None
    hints_used: int
    feedback: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Session Schemas ---
class InterviewSessionCreate(BaseModel):
    role: str
    difficulty: str
    type: str
    mode: str

class InterviewSessionResponse(BaseModel):
    id: str
    role: str
    difficulty: str
    type: str
    mode: str
    created_at: datetime
    status: str
    overall_score: Optional[float] = None
    technical_score: Optional[float] = None
    communication_score: Optional[float] = None
    confidence_score: Optional[float] = None
    fluency_score: Optional[float] = None
    hr_score: Optional[float] = None
    detailed_feedback: Optional[str] = None
    learning_roadmap: Optional[str] = None
    questions: List[InterviewQuestionResponse] = []

    class Config:
        from_attributes = True

# --- Resume Analysis Schemas ---
class ResumeAnalysisResponse(BaseModel):
    id: int
    filename: str
    ats_score: int
    missing_keywords: Optional[str] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    parsed_skills: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Career Chat Schemas ---
class CareerChatCreate(BaseModel):
    message: str

class CareerChatResponse(BaseModel):
    id: int
    role: str
    message_text: str
    created_at: datetime

    class Config:
        from_attributes = True
