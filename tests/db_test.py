import fractions
import sys
import os
import pytest
from typing import Callable
sys.path.append(os.path.join(sys.path[0], '..'))

from recipedb import RecipeDB, Recipe, Ingredient
from exceptions import NameTakenError

i0 = [Ingredient('Egg', 'eggs', 2), Ingredient('Mozzarella', 'handful', 1), Ingredient('Salt', 'teaspoon', 1)]
i1 = [Ingredient('Egg', 'eggs', 3), Ingredient('Salt', 'teaspoon', 1)]
i1_alt = [Ingredient('Egg', 'eggs', 4), Ingredient('Salt', 'teaspoon', fractions.Fraction(1,8))]

r0 = Recipe('Omelette', i0, ['Break and beat eggs with fork', 'add salt', 'let cook in a pan', 'add cheese and fold'], "Don't turn the stove up too much")
r1 = Recipe('Scrambled Eggs', i1, ['Break and beat eggs with fork, adding salt', 'fry in pan and tear into little pieces'])
r1_alt = Recipe('Better Scrambled Eggs', i1_alt, ['Break and beat eggs with fork, adding salt', 'fry in pan and divide up to avoid getting an omelette'], notes="Remove egg from shell before beating it (not the shell) with a fork", myId=r1.id)


TEST_FILE = 'testing.db'

def prep(func: Callable[[], None]):
    def wrapper():
        if os.path.isfile(TEST_FILE):
            os.remove(TEST_FILE)
        RecipeDB.createTable(TEST_FILE)

        func()

    return wrapper

@prep
def test_1():
    with RecipeDB(TEST_FILE) as rdb:
        assert len(rdb) == 0

        rdb.addRecipe(r0)

        assert len(rdb) == 1

        recipe = rdb[r0.id]

        assert recipe == r0
        assert recipe.ingredients == i0

        rdb.clear()

        assert len(rdb) == 0

@prep
def test_2():
    with RecipeDB(TEST_FILE) as rdb:
        rdb.addRecipe(r0)

        with pytest.raises(KeyError):
            rdb[r1.id] = r1 # set item is only for modifying, not adding new entries

        rdb.addRecipe(r1)

        assert len(rdb) == 2

        assert rdb[r0.id] == r0
        assert rdb[r1.id] == r1
        assert rdb[r0.id] != r1
        assert rdb[r1.id] != r0

@prep
def test_delete():
    with RecipeDB(TEST_FILE) as rdb:
        assert len(rdb) == 0

        rdb.addRecipe(r0)
        rdb.addRecipe(r1)

        assert len(rdb) == 2

        assert set(rdb.getNames()) == {r1.recipeName, r0.recipeName}

        assert set(rdb.getNamesAndIDs()) == {(r0.id, r0.recipeName), (r1.id, r1.recipeName)}

        recipe = rdb[r0.id]

        assert recipe == r0
        assert recipe.ingredients == i0

        del rdb[r0.id]

        assert len(rdb) == 1

        assert list(rdb.getNames()) == [r1.recipeName]

@prep
def test_add():
    with RecipeDB(TEST_FILE) as rdb:
        rdb.addRecipe(r0)
        rdb.addRecipe(r1)
        
        with pytest.raises(KeyError):
            rdb.addRecipe(r0)
        
        rTemp = Recipe(r1.recipeName, [], [], "")

        with pytest.raises(NameTakenError):
            rdb.addRecipe(rTemp)
        
        del rdb[r1.id]

        rdb.addRecipe(rTemp)

@prep
def test_update():
    with RecipeDB(TEST_FILE) as rdb:
        rdb.addRecipe(r0)
        rdb.addRecipe(r1)

        assert rdb[r1.id] == r1

        rdb[r1_alt.id] = r1_alt

        assert rdb[r1.id] != r1

        assert rdb[r1.id] == r1_alt
        assert rdb[r1.id].ingredients == i1_alt

        assert len(rdb) == 2