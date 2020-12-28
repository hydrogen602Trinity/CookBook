from __future__ import annotations
from fractions import Fraction
from typing import List # List[int]
import uuid
import base64
import json

class Ingredient:

    def __init__(self, name: str, unit: str, amount: Fraction):
        self.name: str = name
        self.unit: str = unit
        self.amount: Fraction = amount


class Recipe:

    def __init__(self, recipeName: str, ingredients: List[Ingredient], instructions: List[str], notes: str = "", myId:str = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode() ):
        self.recipeName: str = recipeName
        self.ingredients: List[Ingredient] = ingredients
        self.instructions: List[str] = instructions
        self.notes: str = notes 
        self.id: str = myId
    
    def toJson(self) -> str:
        return json.dumps(self.__dict__)

    @staticmethod
    def fromJson(jsonStr: str) -> Recipe:
        temp = json.loads(jsonStr)
        name = temp["recipeName"]
        ingredients = temp["ingredients"]
        instructions = temp["instructions"]
        notes = temp["notes"]
        

        assert isinstance(name, str)
        assert name != ""
        #Need to finish Ingredients 
        for i in instructions:
            assert isinstance(i, str)
        assert instructions != []
        assert isinstance(notes, str)

        if "id" in temp:
            myId = temp["id"]
            #Check that id is a base 64 url safe 
            return Recipe(name, ingredients, instructions, notes, myId)
        else:
            return Recipe(name, ingredients, instructions, notes)

