from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.services.pdf_service import PDFService

router = APIRouter(prefix="/report")

pdf_service = PDFService()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{conversation_id}")
def generate_report(conversation_id: int, db: Session = Depends(get_db)):

    file_path = pdf_service.generate_conversation_pdf(
        db,
        conversation_id
    )

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=file_path
    )