from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from app.database import Base

class NLPResult(Base):

    __tablename__ = "nlp_analysis"

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey("messages.id"))
    summary = Column(Text)
    translation = Column(Text)
    keywords = Column(ARRAY(Text))
    sentiment = Column(Text)