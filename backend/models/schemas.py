from pydantic import BaseModel
from typing import Optional


class CandidateBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    certifications: Optional[str] = None
    interests: Optional[str] = None
    personality_traits: Optional[str] = None
    test_personality_traits: Optional[str] = None
    cv_filename: Optional[str] = None


class CandidateCreate(CandidateBase):
    pass


class CandidateResponse(CandidateBase):
    id: int

    class Config:
        from_attributes = True  # Changed from orm_mode to from_attributes


class JobBase(BaseModel):
    title: str
    description: Optional[str] = None
    required_skills: Optional[str] = None
    required_experience: Optional[str] = None
    required_education: Optional[str] = None
    required_certifications: Optional[str] = None
    required_personality_traits: Optional[str] = None


class JobCreate(JobBase):
    pass


class JobResponse(JobBase):
    id: int

    class Config:
        from_attributes = True  # Changed from orm_mode to from_attributes