from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.nlp_result import NLPResult
from datetime import datetime

class SearchService:

    def get_all_conversations(self, db):
        conversations = db.query(Conversation).all()
        return conversations
    
    def get_full_conversation(self, db: Session, conversation_id: int):

        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).all()

        conversation_data = []

        for msg in messages:

            nlp = db.query(NLPResult).filter(
                NLPResult.message_id == msg.id
            ).first()

            conversation_data.append({
                "message_id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at,
                "nlp": {
                    "summary": nlp.summary if nlp else None,
                    "translation": nlp.translation if nlp else None,
                    "keywords": nlp.keywords if nlp else None,
                    "sentiment": nlp.sentiment if nlp else None
                }
            })

        return conversation_data

    def search_by_user(self, db: Session, user_id: int):

        conversations = db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).all()

        return conversations


    def search_by_date(self, db: Session, start_date: str, end_date: str):

        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

        conversations = db.query(Conversation).filter(
            Conversation.start_time >= start,
            Conversation.start_time <= end
        ).all()

        return conversations


    def search_by_keyword(self, db: Session, keyword: str):

        messages = db.query(Message).filter(
            Message.content.ilike(f"%{keyword}%")
        ).all()

        return messages