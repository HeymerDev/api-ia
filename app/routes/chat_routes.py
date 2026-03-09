from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.ai_service import AIService
from app.services.nlp_service import NLPService
from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService
from app.services.nlp_results_service import NLPResultService

router = APIRouter()

ai = AIService()
nlp = NLPService()
conversation_service = ConversationService()
message_service = MessageService()
nlp_result_service = NLPResultService()


# -----------------------------
# MODELO PARA POST /chat
# -----------------------------
class ChatRequest(BaseModel):
    message: str
    user_id: int
    conversation_id: int | None = None


# -----------------------------
# RUTA CHAT
# -----------------------------
@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):

    message = request.message
    user_id = request.user_id
    conversation_id = request.conversation_id

    # 1️⃣ crear conversación si no existe
    if not conversation_id:
        conversation = conversation_service.create_conversation(
            db,
            user_id=user_id,
            title=message[:30]
        )
        conversation_id = conversation.id

    # 2️⃣ guardar mensaje del usuario
    user_message = message_service.create_message(
        db,
        conversation_id,
        "user",
        message
    )

    # 3️⃣ análisis NLP del mensaje
    nlp_result = nlp.analyze(message)

    # 4️⃣ guardar resultado NLP
    nlp_result_service.create_result(
        db=db,
        message_id=user_message.id,
        keywords=str(nlp_result["keywords"]),
        sentiment=None,
        summary=None,
        translation=None
    )

    # 5️⃣ llamar a la IA
    ai_response = ai.ask(message)

    # 6️⃣ guardar respuesta de la IA
    assistant_message = message_service.create_message(
        db,
        conversation_id,
        "assistant",
        ai_response["response"]
    )

    return {
        "conversation_id": conversation_id,
        "question": message,
        "response": ai_response,
        "nlp": nlp_result
    }