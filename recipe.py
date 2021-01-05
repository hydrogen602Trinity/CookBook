from __future__ import annotations
from fractions import Fraction
import fractions
from typing import Dict, List, Union, Iterator # List[int]
import uuid
import base64
import json
import sqlite3
import atexit
from collections.abc import MutableMapping

class Ingredient:

    def __init__(self, name: str, unit: str, amount: Fraction):
        self.name: str = name
        self.unit: str = unit
        self.amount: Fraction = amount
    
    @staticmethod
    def fromJson(data: Union[str, dict]) -> Ingredient:
        if isinstance(data, str):
            data = json.loads(data)
        assert isinstance(data, dict)
        
        name = data['name']
        unit = data['unit']
        amount = data['amount']
        assert isinstance(name, str) and name != ''
        assert isinstance(unit, str) and unit != ''
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


class Recipe:

    def __init__(self, recipeName: str, ingredients: List[Ingredient], instructions: List[str], notes: str = "", myId:str = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode()):
        self.recipeName: str = recipeName
        self.ingredients: List[Ingredient] = ingredients
        self.instructions: List[str] = instructions
        self.notes: str = notes 
        self.id: str = myId

    def toJson(self) -> str:
        return json.dumps(self.__dict__, default=jsonEncoderHelper)

    @staticmethod
    def fromJson(jsonStr: str) -> Recipe:
        temp = json.loads(jsonStr)
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
    else:
        raise TypeError


class RecipeDB(MutableMapping):

    def __init__(self, dbFileName: str) -> None:
        self.__conn: sqlite3.Connection = sqlite3.connect(dbFileName)
        atexit.register(self.__cleanup)

        self.__cur: sqlite3.Cursor = self.__conn.cursor()

        # self.__cur.execute('DROP TABLE IF EXISTS recipes')
        self.__cur.execute('''
        CREATE TABLE recipes (
            recipeID TEXT NOT NULL,
            name TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            notes TEXT NOT NULL
        )
        ''')
        self.__conn.commit()

    def __cleanup(self):
        # self.__cur.execute('DROP TABLE IF EXISTS recipes')
        self.__conn.commit()
        self.__conn.close()

    def __getitem__(self, recipeID: str) -> Recipe:
        ...

    def __setitem__(self, recipeID: str, val: Recipe) -> None:
        ...
    
    def __delitem__(self, recipeID: str) -> None:
        ...
    
    def __iter__(self) -> Iterator[str]:
        ...
    
    def __len__(self) -> int:
        ...
