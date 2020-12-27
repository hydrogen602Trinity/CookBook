from fractions import Fraction
from typing import List # List[int]
import uuid


class Ingredient:

    def __init__(self, name: str, unit: str, amount: Fraction):
        self.name: str = name
        self.unit: str = unit
        self.amount: Fraction = amount


class Recipe:

    def __init__(self, recipeName: str, ingredients: List[Ingredient], instructions: List[str], notes: str = ""):
        self.recipeName: str = recipeName
        self.ingredients: List[Ingredient] = ingredients
        self.instructions: List[str] = instructions
        self.notes: str = notes 
        self.id: uuid.UUID = uuid.uuid4()
        
        