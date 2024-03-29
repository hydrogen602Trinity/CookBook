from __future__ import annotations
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
# from sqlalchemy.orm import backref
from sqlalchemy.sql import expression
from fractions import Fraction
from flask_login import UserMixin
from werkzeug.security import generate_password_hash


from database import db

if TYPE_CHECKING:
    from datetime import date


# class Note(db.Model):

#     __tablename__ = 'note'

#     id: int = db.Column(db.Integer, primary_key=True)
#     content: str = db.Column(db.String(4096))

#     def __init__(self, content: str) -> None:
#         self.content = content
#         super().__init__()

#     def toJson(self) -> Dict[str, Any]:
#         d = {}
#         for col in self.__table__.columns:
#             d[col.description] = getattr(self, col.description)
#         return d


recipeTags = db.Table('recipeTags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True)
)

class Recipe(db.Model):

    __tablename__ = 'recipe'
    # nullable=True is only until we having proper test data

    id: int = db.Column(db.Integer, primary_key=True)
    ingredients: List[Ingredient] = db.relationship('Ingredient', backref='recipe', cascade='all, delete, delete-orphan', passive_deletes=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user: User
    name: str = db.Column(db.String(128), nullable=False)
    courseType: str = db.Column(db.String(15), nullable=True)
    style: str = db.Column(db.String(10), nullable=True)
    prepTime: int = db.Column(db.Integer, db.CheckConstraint('0 <= "prepTime"'), nullable=True)
    difficulty: int = db.Column(db.Integer, nullable=True)
    rating: int = db.Column(db.Integer, db.CheckConstraint('1 <= rating AND rating <= 5'), nullable=True)
    notes: str = db.Column(db.String(4096), nullable=False)
    deleted: bool = db.Column(db.Boolean, server_default=expression.false(), nullable=False)

    recipe_Tags: List[Tag] = db.relationship('Tag', secondary=recipeTags, back_populates="assocRecipes")
    meals: List[Meal] = db.relationship('Meal', backref='recipe', cascade='all, delete, delete-orphan', passive_deletes=True)

    def __init__(self, name: str, notes: str, ingredients: List[Ingredient], user: User, 
                 courseType: Optional[str] = None, style: Optional[str] = None, 
                 prepTime: Optional[int] = None, difficulty: Optional[int] = None, 
                 rating: Optional[int] = None) -> None:
        self.name = name
        self.user_id = user.id
        self.notes = notes
        self.ingredients = ingredients
        self.courseType = courseType
        self.style = style
        self.prepTime = prepTime
        self.difficulty = difficulty if difficulty else None
        self.rating = rating
        self.recipe_Tags = []
    
    def __repr__(self) -> str:
        return f'Recipe(id={self.id}, name={self.name})'

    def toJson(self, minimum: bool = False) -> Dict[str, Any]:
        if minimum:
            return {
                'id': self.id,
                'name': self.name
            }
        else:
            return {
                'id': self.id,
                'name': self.name,
                'notes': self.notes,
                'recipeTags': [i.toJson() for i in self.recipe_Tags],
                'ingredients': [i.toJson() for i in self.ingredients],
                'rating': self.rating,
                'prepTime': self.prepTime
            }

class Ingredient(db.Model):

    __tablename__ = 'ingredient'

    id: int = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id', ondelete='CASCADE'), nullable=False)
    recipe: Recipe  # created in class Recipe using backref
    name: str = db.Column(db.String(128))

    # use amount, not _num, _denom when dealing with the amount
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
    
    def toJson(self, noID: bool = False) -> Dict[str, Any]:
        if noID:
            return {
                'name': self.name,
                'num': self._num,
                'denom': self._denom,
                'unit': self.unit
            }
        else:
            return {
                'id': self.id,
                'name': self.name,
                'num': self._num,
                'denom': self._denom,
                'unit': self.unit
            }


userTags = db.Table('userTags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(UserMixin, db.Model):

    __tablename__ = 'user'

    id: int = db.Column(db.Integer, primary_key=True)

    user_Tags: List[Tag] = db.relationship('Tag', secondary=userTags, back_populates="assocUsers")
    recipes: List[Recipe] = db.relationship('Recipe', backref='user', cascade='all, delete', passive_deletes=True)
    meals: List[Meal] = db.relationship('Meal', backref='user', cascade='all, delete', passive_deletes=True)

    name: str = db.Column(db.String(128))
    email: str = db.Column(db.String(128), unique=True)
    password: str = db.Column(db.String(100))
    is_admin: bool = db.Column(db.Boolean)

    def __init__(self, name: str, email: str, password: str, is_admin: bool = False) -> None: 
        #meals: Optional[List[Meal]] = None) -> None:
        self.name = name
        self.email = email
        self.password = generate_password_hash(password, method='sha256')
        self.is_admin = is_admin
        self.user_Tags = []
        #self.meals = meals if meals else None

    def __repr__(self) -> str:
        return f'User(id={self.id}, name={self.name}, email={self.email})'
    
    def toJson(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'userTags': [i.toJson() for i in self.user_Tags]
        }

class Tag(db.Model):

    __tablename__ = 'tag'

    id: int = db.Column(db.Integer, primary_key=True)
    assocUsers: List[User] = db.relationship('User', secondary=userTags, back_populates="user_Tags")
    assocRecipes: List[Recipe] = db.relationship('Recipe', secondary=recipeTags, back_populates="recipe_Tags")
    tagType: str = db.Column(db.String(20))

    def __init__(self, tagType: str, assocUsers: Optional[List[User]] = None, 
            assocRecipes: Optional[List[Recipe]] = None) -> None:
        self.tagType = tagType
        self.assocUsers = assocUsers if assocUsers else []
        self.assocRecipes = assocRecipes if assocRecipes else []

    def __repr__(self) -> str:
        return f'Tag(id={self.id}, tagType={self.tagType})'

    def toJson(self, showAssociates: bool = False) -> Dict[str, Any]:
        if showAssociates:
            return {
                'id': self.id,
                'tagType': self.tagType,
                'assocUsers': [i.toJson() for i in self.assocUsers],
                'assocRecipes': [i.toJson(minimum=True) for i in self.assocRecipes]
            }
        else:
            return {
                'id': self.id,
                'tagType': self.tagType
            }

class Meal(db.Model):

    __tablename__ = 'meal'

    id: int = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user: User
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id', ondelete='CASCADE'), nullable=False)
    recipe: Recipe
    label: str = db.Column(db.String(20))
    day: str = db.Column(db.Date)

    def __init__(self, label: str, day: date, user: Union[User, int], recipe: Union[Recipe, int]) -> None:
        self.label = label
        self.day = day
        self.user_id = user if isinstance(user, int) else user.id
        self.recipe_id = recipe if isinstance(recipe, int) else recipe.id

    def __repr__(self) -> str:
        return f'Meal(id={self.id}, label={self.label}, day={self.day})'

    def toJson(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'label': self.label,
            'day': self.day.isoformat(),
            'user_id': self.user_id,
            'recipe_id': self.recipe_id
            # 'recipe_name': self.recipe.name
        }
