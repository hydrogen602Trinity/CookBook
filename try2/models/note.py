from typing import Any, Dict, List
from database import db


class Note(db.Model):

    __tablename__ = "note"

    id: int = db.Column(db.Integer, primary_key=True)
    content: str = db.Column(db.String(4096))

    def __init__(self, content: str) -> None:
        self.content = content
        super().__init__()

    def toJson(self) -> Dict[str, Any]:
        d = {}
        for col in self.__table__.columns:
            d[col.description] = getattr(self, col.description)
        return d
