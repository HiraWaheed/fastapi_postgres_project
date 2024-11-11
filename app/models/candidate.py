from app.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    experience = Column(Integer)
