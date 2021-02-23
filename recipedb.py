import sqlite3
import fractions
import json
from collections.abc import MutableMapping
from typing import Iterator, List, Optional, Tuple, Type
from recipe import Recipe, Ingredient
from exceptions import NameTakenError


class IngredientsDB:

    def __init__(self, dbFileName: str) -> None:
        self.__conn: Optional[sqlite3.Connection] = None
        self.__dbFileName: str = dbFileName

        self.__cur: Optional[sqlite3.Cursor] = None
        
    def __enter__(self):
        self.__conn = sqlite3.connect(self.__dbFileName)
        self.__cur = self.__conn.cursor()
        return self

    @staticmethod
    def createTable(dbFileName: str):
        conn = sqlite3.connect(dbFileName)
        cur = conn.cursor()

        cur.execute('PRAGMA foreign_keys = ON;')
        conn.commit()

        cur.execute('PRAGMA foreign_keys;')
        assert cur.fetchone() == (1,) # foreign keys enabled
        cur.execute('DROP TABLE IF EXISTS ingredients')
        cur.execute('''
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
        conn.commit()
        conn.close()

    def __exit__(self, exc_type: Type[BaseException], exc_value: BaseException, traceback):
        if self.__cur is None or self.__conn is None:
            raise RuntimeError("Not yet connected to database")

        self.__conn.commit()
        self.__conn.close()

    def __getitem__(self, recipeID: str) -> List[Ingredient]:
        if self.__cur is None or self.__conn is None:
            raise RuntimeError("Not yet connected to database")

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
    
    def __setitem__(self, recipeID: str, ingredients: List[Ingredient]) -> None:
        self.__delitem__(recipeID)
        self.addIngredients(recipeID, ingredients)

    def addIngredients(self, recipeID: str, ingredients: List[Ingredient]) -> None:
        if self.__cur is None or self.__conn is None:
            raise RuntimeError("Not yet connected to database")

        for ingredient in ingredients:
            sql = '''INSERT INTO ingredients(name,unit,amountNumerator, amountDenominator, recipeID)
            VALUES(?,?,?,?,?)'''
            self.__cur.execute(sql, (ingredient.name, ingredient.unit, ingredient.amount.numerator, ingredient.amount.denominator, recipeID))
        self.__conn.commit()

    def __delitem__(self, recipeID: str) -> None:
        if self.__cur is None or self.__conn is None:
            raise RuntimeError("Not yet connected to database")

        sql = '''DELETE FROM ingredients WHERE recipeID=?'''
        self.__cur.execute(sql, (recipeID,))
        self.__conn.commit()

    def deleteItems(self, recipeID: str) -> None:
        self.__delitem__(recipeID)


class RecipeDB(MutableMapping):

    def __init__(self, dbFileName: str) -> None:
        self.__conn: Optional[sqlite3.Connection] = None
        self.__dbFileName: str = dbFileName
        self.__cur: Optional[sqlite3.Cursor] = None

        # self.__cur: sqlite3.Cursor = self.__conn.cursor()

        # self.__cur.execute('DROP TABLE IF EXISTS recipes')
        # self.__cur.execute('''
        # CREATE TABLE IF NOT EXISTS recipes (
        #     recipeID TEXT NOT NULL UNIQUE,
        #     name TEXT NOT NULL,
        #     instructions TEXT NOT NULL,
        #     notes TEXT NOT NULL
        # )
        # ''')
        # self.__conn.commit()

        self.__ingredientsDB = IngredientsDB(dbFileName)

    @staticmethod
    def createTable(dbFileName: str):
        conn = sqlite3.connect(dbFileName)
        cur = conn.cursor()
        cur.execute('DROP TABLE IF EXISTS recipes')
        cur.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            recipeID TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL UNIQUE,
            instructions TEXT NOT NULL,
            notes TEXT NOT NULL
        )
        ''')
        conn.commit()
        conn.close()
        print('Created recipes table')
        IngredientsDB.createTable(dbFileName)

    def __enter__(self):
        print(self.__dbFileName)
        self.__conn: sqlite3.Connection = sqlite3.connect(self.__dbFileName)
        self.__cur: sqlite3.Cursor = self.__conn.cursor()
        self.__ingredientsDB.__enter__()
        return self

    def __exit__(self, exc_type: Type[BaseException], exc_value: BaseException, traceback):
        if self.__cur is None or self.__conn is None:
            raise RuntimeError("Not yet connected to database")

        self.__conn.commit()
        self.__conn.close()
        self.__ingredientsDB.__exit__(exc_type, exc_value, traceback)

    def __getitem__(self, recipeID: str) -> Recipe:
        if self.__cur is None or self.__conn is None:
            raise RuntimeError("Not yet connected to database")

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
        '''
        Only for modifying recipes. Use addRecipe for adding a new entry
        '''
        if self.__cur is None or self.__conn is None:
            raise RuntimeError("Not yet connected to database")

        oldRecipe = self.__getitem__(recipeID)

        assert recipeID == val.id
        assert isinstance(val.recipeName, str) and len(val.recipeName) > 0
        assert all(map(lambda x: isinstance(x, str), val.instructions))
        assert isinstance(val.notes, str)

        sql = 'UPDATE recipes SET name=?, instructions=?, notes=? WHERE recipeID=?'

        self.__cur.execute(sql, (val.recipeName, json.dumps(val.instructions), val.notes, val.id))
        self.__conn.commit()

        self.__ingredientsDB[recipeID] = val.ingredients

    def addRecipe(self, val: Recipe) -> None:
        if self.__cur is None or self.__conn is None:
            raise RuntimeError("Not yet connected to database")

        sql = 'SELECT name FROM recipes WHERE recipeID=?'
        self.__cur.execute(sql, (val.id,))
        row = self.__cur.fetchone()
        if row is not None:
            raise KeyError(f'recipeID already exists: {val.id}')

        sql = 'SELECT recipeID FROM recipes WHERE name=?'
        self.__cur.execute(sql, (val.recipeName,))
        row = self.__cur.fetchone()
        if row is not None:
            raise NameTakenError(f'Name already exists: {val.recipeName}')

        assert isinstance(val.recipeName, str) and len(val.recipeName) > 0
        assert all(map(lambda x: isinstance(x, str), val.instructions))
        assert isinstance(val.notes, str)

        sql = 'INSERT INTO recipes (recipeID, name, instructions, notes) VALUES (?, ?, ?, ?)'
        self.__cur.execute(sql, (val.id, val.recipeName, json.dumps(val.instructions), val.notes))
        self.__conn.commit()

        self.__ingredientsDB.addIngredients(val.id, val.ingredients)

    def __delitem__(self, recipeID: str) -> None:
        if self.__cur is None or self.__conn is None:
            raise RuntimeError("Not yet connected to database")

        sql = 'DELETE FROM recipes WHERE recipeID=?'
        self.__cur.execute(sql, (recipeID,))
        self.__conn.commit()

    def clear(self) -> None:
        if self.__cur is None or self.__conn is None:
            raise RuntimeError("Not yet connected to database")

        sql = 'DELETE FROM recipes'
        self.__cur.execute(sql)
        self.__conn.commit()

    def __iter__(self) -> Iterator[str]:
        if self.__cur is None or self.__conn is None:
            raise RuntimeError("Not yet connected to database")

        sql = 'SELECT recipeID FROM recipes'
        self.__cur.execute(sql)
        ls = self.__cur.fetchall()
        return map(lambda x: x[0], ls)

    def getNames(self) -> Iterator[str]:
        if self.__cur is None or self.__conn is None:
            raise RuntimeError("Not yet connected to database")

        sql = 'SELECT name FROM recipes'
        self.__cur.execute(sql)
        ls = self.__cur.fetchall()
        return map(lambda x: x[0], ls)
    
    def getNamesAndIDs(self) -> List[Tuple[str, str]]:
        if self.__cur is None or self.__conn is None:
            raise RuntimeError("Not yet connected to database")
        
        sql = 'SELECT recipeID, name FROM recipes'
        self.__cur.execute(sql)
        ls = self.__cur.fetchall()
        return ls

    def __len__(self) -> int:
        if self.__cur is None or self.__conn is None:
            raise RuntimeError("Not yet connected to database")

        sql = 'SELECT COUNT(*) FROM recipes'
        self.__cur.execute(sql)
        count, = self.__cur.fetchone()
        assert isinstance(count, int)
        return count


if __name__ == '__main__':
    r = RecipeDB('test.db')