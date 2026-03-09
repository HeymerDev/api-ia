from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session
from app.models.message import Message


class PDFService:

    def generate_conversation_pdf(self, db: Session, conversation_id: int):

        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).all()

        file_name = f"conversation_{conversation_id}.pdf"

        c = canvas.Canvas(file_name)

        y = 800

        c.setFont("Helvetica", 12)

        c.drawString(200, 820, f"Conversation Report #{conversation_id}")

        for msg in messages:

            line = f"{msg.role}: {msg.content}"

            c.drawString(50, y, line)

            y -= 20

            if y < 50:
                c.showPage()
                y = 800

        c.save()

        return file_name