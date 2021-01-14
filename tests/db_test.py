import sys, os
sys.path.append(os.path.join(sys.path[0], '..'))

from recipe import RecipeDB, Recipe, Ingredient

i0 = [Ingredient('Egg', 'eggs', 2), Ingredient('Mozzarella', 'handful', 1), Ingredient('Salt', 'teaspoon', 1)]
i1 = [Ingredient('Egg', 'eggs', 3), Ingredient('Salt', 'teaspoon', 1)]

r0 = Recipe('Omelette', i0, ['Break and beat eggs with fork', 'add salt', 'let cook in a pan', 'add cheese and fold'], "Don't turn the stove up too much")
r1 = Recipe('Scrambled Eggs', i1, ['Break and beat eggs with fork, adding salt', 'fry in pan and tear into little pieces'])

TEST_FILE = 'testing.db'


def test_1():
    if os.path.isfile(TEST_FILE):
        os.remove(TEST_FILE)
    rdb = RecipeDB(TEST_FILE)
    assert len(rdb) == 0

    rdb.addRecipe(r0)

    assert len(rdb) == 1

    recipe = rdb[r0.id]

    assert recipe == r0
    assert recipe.ingredients == i0

    rdb.clear()

    assert len(rdb) == 0

def test_2():
    if os.path.isfile(TEST_FILE):
        os.remove(TEST_FILE)
    rdb = RecipeDB(TEST_FILE)

    rdb.addRecipe(r0)
    rdb[r1.id] = r1

    assert len(rdb) == 2

    assert rdb[r0.id] == r0
    assert rdb[r1.id] == r1
    assert rdb[r0.id] != r1
    assert rdb[r1.id] != r0