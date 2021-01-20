import sqlite3
import atexit
import fractions
import json
from collections.abc import MutableMapping
from typing import Iterator, List
from recipe import Recipe, Ingredient


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
    
    def getNames(self) -> Iterator[str]:
        sql = 'SELECT name FROM recipes'
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