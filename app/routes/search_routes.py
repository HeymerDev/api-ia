from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.search_service import SearchService

router = APIRouter(prefix="/search")

search_service = SearchService()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/conversations")
def get_all_conversations(db: Session = Depends(get_db)):

    results = search_service.get_all_conversations(db)

    return results

@router.get("/conversation/{conversation_id}")
def get_full_conversation(conversation_id: int, db: Session = Depends(get_db)):

    result = search_service.get_full_conversation(
        db,
        conversation_id
    )

    return {
        "conversation_id": conversation_id,
        "messages": result
    }


# Buscar conversaciones por usuario
@router.get("/user/{user_id}")
def search_user(user_id: int, db: Session = Depends(get_db)):

    results = search_service.search_by_user(db, user_id)

    return results


# Buscar por rango de fecha
@router.get("/date")
def search_date(start_date: str, end_date: str, db: Session = Depends(get_db)):

    results = search_service.search_by_date(db, start_date, end_date)

    return results


# Buscar por palabra clave
@router.get("/keyword/{word}")
def search_keyword(word: str, db: Session = Depends(get_db)):

    results = search_service.search_by_keyword(db, word)

    return results