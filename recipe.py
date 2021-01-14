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
            return r.__uuid == self.__uuid
        else:
            return False

    def __ne__(self, r: object) -> bool:
        return not self.__eq__(r)

    @property
    def id(self) -> str:
        return base64.urlsafe_b64encode(self.__uuid.bytes).decode()

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


class IngredientsDB:

    def __init__(self, dbFileName: str) -> None:
        self.__conn: sqlite3.Connection = sqlite3.connect(dbFileName)
        atexit.register(self.__cleanup)

        self.__cur: sqlite3.Cursor = self.__conn.cursor()

        self.__cur.execute('PRAGMA foreign_keys = ON;')
        self.__conn.commit()

        self.__cur.execute('PRAGMA foreign_keys;')
        assert self.__cur.fetchone() == (1,) # foreign keys enabled

        self.__cur.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            name     TEXT NOT NULL,
            unit     TEXT NOT NULL,
            amountNumerator   INT NOT NULL,
            amountDenominator INT NOT NULL,
            recipeID INT NOT NULL,
            FOREIGN KEY (recipeID)
                REFERENCES recipes (recipeID) 
                    ON UPDATE CASCADE
                    ON DELETE CASCADE
        )
        ''')
        self.__conn.commit()

    def __cleanup(self):
        self.__conn.commit()
        self.__conn.close()

    def __getitem__(self, recipeID: str) -> List[Ingredient]:
        self.__cur.execute('SELECT name, unit, amountNumerator, amountDenominator FROM ingredients WHERE recipeID=?', (recipeID,))

        output = []
        row = self.__cur.fetchone()
        while row is not None:
            name, unit, amountNum, amountDenom = row
            assert isinstance(name, str) and len(name) > 0
            assert isinstance(unit, str)
            assert isinstance(amountNum, int)
            assert isinstance(amountDenom, int)
            output.append(Ingredient(name, unit, fractions.Fraction(amountNum, amountDenom)))

            row = self.__cur.fetchone()

        return output

    def addIngredients(self, recipeID: str, ingredients: List[Ingredient]) -> None:
        for ingredient in ingredients:
            sql = '''INSERT INTO ingredients(name,unit,amountNumerator, amountDenominator, recipeID)
            VALUES(?,?,?,?,?)'''
            self.__cur.execute(sql, (ingredient.name, ingredient.unit, ingredient.amount.numerator, ingredient.amount.denominator, recipeID))
        self.__conn.commit()

    def __delitem__(self, recipeID: str) -> None:
        sql = '''DELETE FROM ingredients WHERE recipeID=?'''
        self.__cur.execute(sql, (recipeID,))
        self.__conn.commit()

    def deleteItems(self, recipeID: str) -> None:
        self.__delitem__(recipeID)


class RecipeDB(MutableMapping):

    def __init__(self, dbFileName: str) -> None:
        self.__conn: sqlite3.Connection = sqlite3.connect(dbFileName)
        atexit.register(self.__cleanup)

        self.__cur: sqlite3.Cursor = self.__conn.cursor()

        # self.__cur.execute('DROP TABLE IF EXISTS recipes')
        self.__cur.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            recipeID TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            instructions TEXT NOT NULL,
            notes TEXT NOT NULL
        )
        ''')
        self.__conn.commit()

        self.__ingredientsDB = IngredientsDB(dbFileName)

    def __cleanup(self):
        self.__conn.commit()
        self.__conn.close()

    def __getitem__(self, recipeID: str) -> Recipe:
        sql = 'SELECT name, instructions, notes FROM recipes WHERE recipeID=?'
        self.__cur.execute(sql, (recipeID,))
        row = self.__cur.fetchone()
        if row is None:
            raise KeyError(recipeID)
        name, instructions, notes = row
        assert isinstance(name, str) and len(name) > 0
        assert isinstance(instructions, str)
        assert isinstance(notes, str)

        ls: List[str] = json.loads(instructions)
        assert isinstance(ls, list)
        assert all(isinstance(e, str) for e in ls)

        ingredients = self.__ingredientsDB[recipeID]

        return Recipe(name, ingredients, ls, notes, recipeID)

    def __setitem__(self, recipeID: str, val: Recipe) -> None:
        assert recipeID == val.id
        
        sql = 'INSERT INTO recipes (recipeID, name, instructions, notes) VALUES (?, ?, ?, ?)'
        self.__cur.execute(sql, (recipeID, val.recipeName, json.dumps(val.instructions), val.notes))
        self.__conn.commit()

        self.__ingredientsDB.addIngredients(recipeID, val.ingredients)

    def addRecipe(self, val: Recipe) -> None:
        self.__setitem__(val.id, val)

    def __delitem__(self, recipeID: str) -> None:
        sql = 'DELETE FROM recipes WHERE recipeID=?'
        self.__cur.execute(sql, (recipeID,))
        self.__conn.commit()
    
    def clear(self) -> None:
        sql = 'DELETE FROM recipes'
        self.__cur.execute(sql)
        self.__conn.commit()

    def __iter__(self) -> Iterator[str]:
        sql = 'SELECT recipeID FROM recipes'
        self.__cur.execute(sql)
        ls = self.__cur.fetchall()
        return map(lambda x: x[0], ls)

    def __len__(self) -> int:
        sql = 'SELECT COUNT(*) FROM recipes'
        self.__cur.execute(sql)
        count, = self.__cur.fetchone()
        assert isinstance(count, int)
        return count

if __name__ == '__main__':
    r = RecipeDB('test.db')