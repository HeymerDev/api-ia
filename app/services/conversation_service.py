from sqlalchemy.orm import Session
from app.models.conversation import Conversation

class ConversationService:

    def create_conversation(self, db: Session, user_id: int, title: str = "Nueva conversación"):
        conversation = Conversation(
            user_id=user_id,
            title=title
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        return conversation

    def get_conversation(self, db: Session, conversation_id: int):
        return db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()