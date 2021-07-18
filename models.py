from __future__ import annotations
from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import backref
from fractions import Fraction

from database import db


class Note(db.Model):

    __tablename__ = 'note'

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
    ingredients: List[Ingredient] = db.relationship('Ingredient', 
                                     backref='recipe', 
                                     cascade='all, delete, delete-orphan',
                                     passive_deletes=True)
    name: str = db.Column(db.String(128), nullable=False)
    notes: str = db.Column(db.String(4096), nullable=False)

    def __init__(self, name: str, notes: str, ingredients: List[Ingredient]) -> None:
        self.name = name
        self.notes = notes
        self.ingredients = ingredients
    
    def __repr__(self) -> str:
        return f'Recipe(id={self.id}, name={self.name})'
    
    def toJson(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'notes': self.notes,
            'ingredients': [i.toJson() for i in self.ingredients]
        }


class Ingredient(db.Model):

    __tablename__ = 'ingredient'

    id: int = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, 
                          db.ForeignKey('recipe.id', 
                                        ondelete='CASCADE'), 
                          nullable=False)
    recipe: Recipe  # created in class Recipe using backref
    name: str = db.Column(db.String(128))
    _num: int = db.Column(db.Integer)
    _denom: int = db.Column(db.Integer)
    unit: str = db.Column(db.String(20))

    def __init__(self, name: str, amount: Union[Fraction, int, float, str], unit: Optional[str] = None, recipe_id: Optional[int] = None) -> None:
        if recipe_id:
            self.recipe_id = recipe_id
        self.name = name
        self.amount = amount
        self.unit = unit if unit else None

    def __repr__(self) -> str:
        return f'Ingredient(id={self.id}, name={self.name}, amount={self.amount}, unit={self.unit})'

    @property
    def amount(self) -> Fraction:
        return Fraction(self._num, self._denom)

    @amount.setter
    def amount(self, x: Union[Fraction, int, float, str]) -> None:
        f: Fraction = x if isinstance(x, Fraction) else Fraction(x)
        self._num = f.numerator
        self._denom = f.denominator
    
    def toJson(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'num': self._num,
            'denom': self._denom,
            'unit': self.unit
        }
