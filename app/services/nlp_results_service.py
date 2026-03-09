from typing import List
from app.models.nlp_result import NLPResult

from sqlalchemy.orm import Session

class NLPResultService:

    def create_result(
        self,
        db: Session,
        message_id: int,
        keywords: List[str],  # ⚡ cambiar de str a List[str]
        sentiment: str | None = None,
        summary: str | None = None,
        translation: str | None = None
    ):

        result = NLPResult(
            message_id=message_id,
            keywords=keywords,
            sentiment=sentiment,
            summary=summary,
            translation=translation
        )

        db.add(result)
        db.commit()
        db.refresh(result)

        return result