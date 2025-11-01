from sqlalchemy import Column, Integer, String, Text
from database.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    required_skills = Column(Text, nullable=True)
    required_experience = Column(Text, nullable=True)
    required_education = Column(Text, nullable=True)
    required_certifications = Column(Text, nullable=True)
    required_personality_traits = Column(Text, nullable=True)  # JSON string