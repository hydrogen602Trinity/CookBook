from typing import Any, Dict, List

from sqlalchemy.orm import backref
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


class Recipe(db.Model):

    __tablename__ = 'recipe'

    id: int = db.Column(db.Integer, primary_key=True)
    ingredient_ids = db.relationship('Ingredient', 
                                     backref='recipe', 
                                     cascade="all, delete",
                                     passive_deletes=True)
    
    def __init__(self) -> None:
        pass


class Ingredient(db.Model):

    __tablename__ = "ingredient"

    id: int = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, 
                          db.ForeignKey('recipe.id', 
                                        ondelete="CASCADE"), 
                          nullable=False)
    recipe: Recipe  # created in class Recipe using backref
    name: str = db.Column(db.String(128))
    
    def __init__(self, recipe_id: int, name: str) -> None:
        self.recipe_id = recipe_id
        self.name = name
    
    def __repr__(self) -> str:
        return f'Ingredient(id={self.id}, name={self.name})'


