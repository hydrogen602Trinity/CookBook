from __future__ import annotations
from fractions import Fraction
import fractions
from typing import Dict, List, Union, Any # List[int]
import uuid
import base64
import json


class Ingredient:

    def __init__(self, name: str, unit: str, amount: Union[Fraction, int, float]):
        self.name: str = name
        self.unit: str = unit
        self.amount: Fraction = fractions.Fraction(amount)
    
    @staticmethod
    def fromJson(data: Union[str, dict]) -> Ingredient:
        if isinstance(data, str):
            data = json.loads(data)
        assert isinstance(data, dict)
        
        name = data['name']
        unit = data['unit']
        amount = data['amount']
        assert isinstance(name, str) and name != ''
        assert isinstance(unit, str)  # and unit != ''
        assert isinstance(amount, (str, int, float)) and amount != ''
        amount = fractions.Fraction(amount)
        assert amount > 0

        return Ingredient(name, unit, amount)
    
    def toJsonSerializable(self) -> Dict[str, object]:
        d = dict(self.__dict__)
        d['amount'] = str(d['amount'])
        return d
    
    def toJson(self) -> str:
        return json.dumps(self.toJsonSerializable())

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Ingredient) and o.name == self.name and o.unit == self.unit and o.amount == self.amount
    
    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)


class Recipe:

    # TODO: change from uuid to incrementing int

    def __init__(self, recipeName: str, ingredients: List[Ingredient], instructions: List[str], notes: str = "", myId: Union[str, int, uuid.UUID, None] = None):
        self.recipeName: str = recipeName
        self.ingredients: List[Ingredient] = ingredients
        self.instructions: List[str] = instructions
        self.notes: str = notes

        # print(myId, recipeName)

        self.__uuid: uuid.UUID
        if myId is None:
            self.__uuid = uuid.uuid4()
        elif isinstance(myId, str):
            self.__uuid = uuid.UUID(bytes=base64.urlsafe_b64decode(myId.encode()))
        elif isinstance(myId, int):
            self.__uuid = uuid.UUID(int=myId)
        elif isinstance(myId, uuid.UUID):
            self.__uuid = myId
        else:
            raise TypeError(f"Expected 'str', 'int', 'uuid.UUID', or None but got '{type(myId)}'")

    def __eq__(self, r: object) -> bool:
        if isinstance(r, Recipe):
            return r.__uuid == self.__uuid and r.recipeName == self.recipeName and r.ingredients == self.ingredients and r.instructions == self.instructions and r.notes == self.notes
        else:
            return False

    def __ne__(self, r: object) -> bool:
        return not self.__eq__(r)

    @property
    def id(self) -> str:
        return self.uuidToStr(self.__uuid)

    @staticmethod
    def uuidToStr(u: uuid.UUID) -> str:
        return base64.urlsafe_b64encode(u.bytes).decode()

    def toJson(self) -> str:
        d = dict(self.__dict__)
        for key in self.__dict__:
            if key.startswith('_'):
                del d[key]

        d['id'] = self.id
        return json.dumps(d, default=jsonEncoderHelper)

    @staticmethod
    def fromJson(jsonStr: Union[str, Any]) -> Recipe:
        temp = json.loads(jsonStr) if isinstance(jsonStr, str) else jsonStr
        
        assert isinstance(temp, dict)
        name = temp["recipeName"]
        ingredients = temp["ingredients"]
        instructions = temp["instructions"]
        if "notes" in temp:
            notes = temp["notes"]
        else:
            notes = ''

        assert isinstance(name, str)
        assert name != ""
        #Need to finish Ingredients 
        assert isinstance(ingredients, list)

        ingredients = list(map(Ingredient.fromJson, ingredients))

        assert isinstance(instructions, list)
        for i in instructions:
            assert isinstance(i, str)
        assert instructions != []
        assert isinstance(notes, str)

        if "id" in temp:
            myId = temp["id"]
            assert isinstance(myId, str)

            # verify that the id is correct
            decoded = base64.urlsafe_b64decode(myId.encode())
            assert len(decoded) == 16
            assert base64.urlsafe_b64encode(decoded) == myId.encode()

            return Recipe(name, ingredients, instructions, notes, myId)
        else:
            return Recipe(name, ingredients, instructions, notes)


def jsonEncoderHelper(obj):
    # find some better way?
    if isinstance(obj, Ingredient):
        return obj.toJsonSerializable()
    elif isinstance(obj, fractions.Fraction):
        return str(obj)
    elif isinstance(obj, uuid.UUID):
        return Recipe.uuidToStr(obj)
    else:
        raise TypeError(f"Got unhandled type {type(obj)}")