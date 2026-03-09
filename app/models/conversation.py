from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Conversation(Base):

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    title = Column(String)
    start_time = Column(DateTime, default=func.now())
    end_time = Column(DateTime)