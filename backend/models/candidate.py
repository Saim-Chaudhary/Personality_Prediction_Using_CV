from sqlalchemy import Column, Integer, String, Text
from database.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    skills = Column(Text, nullable=True)
    experience = Column(Text, nullable=True)
    education = Column(Text, nullable=True)
    certifications = Column(Text, nullable=True)
    interests = Column(Text, nullable=True)
    personality_traits = Column(Text, nullable=True)  # JSON string
    test_personality_traits = Column(Text, nullable=True)  # JSON string
    cv_filename = Column(String(255), nullable=True)