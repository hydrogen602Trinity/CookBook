import fractions
from flask.json import jsonify
from recipedb import RecipeDB
from flask import Flask, abort, request
from recipe import Ingredient, Recipe
import os

app = Flask(__name__)

# tempRecipe = recipe.Recipe("Chocolate Milk", [
#     recipe.Ingredient("Milk", "cup", 1), 
#     recipe.Ingredient("Chocolate", "teaspoon", 2)], ["Add chocolate to milk", "Stir"], "Can add more chocolate if desired")
#recipes: Dict[str, recipe.Recipe] = { tempRecipe.id: tempRecipe } # temporary

path: str = 'default.db'
if 'DATABASE_PATH' in os.environ:
    path = os.environ['DATABASE_PATH']


# recipes.addRecipe(tempRecipe)
# print(tempRecipe.id)

RecipeDB.createTable(path)

i0 = [Ingredient('Egg', 'eggs', 2), Ingredient('Mozzarella', 'handful', 1), Ingredient('Salt', 'teaspoon', 1)]
i1 = [Ingredient('Egg', 'eggs', 3), Ingredient('Salt', 'teaspoon', fractions.Fraction(1,8))]

r0 = Recipe('Omelette', i0, ['Break and beat eggs with fork', 'add salt', 'let cook in a pan', 'add cheese and fold'], "Don't turn the stove up too much")
r1 = Recipe('Scrambled Eggs', i1, ['Break and beat eggs with fork, adding salt', 'fry in pan and tear into little pieces'])


with RecipeDB(path) as recipes:
    recipes.addRecipe(r0)
    recipes.addRecipe(r1)

@app.route('/')
def hello_world():
    with open('frontend/test.html') as f:
        return f.read()

@app.route('/recipe/<string:recipeID>', methods = ['GET', 'DELETE'])
def getRecipe(recipeID: str) -> str:
    with RecipeDB(path) as recipes:
        if recipeID in recipes:
            if request.method == 'GET':
                return recipes[recipeID].toJson()
            elif request.method == 'DELETE':
                del recipes[recipeID]
                return ''
            else:
                print(f'Unknown method: "{request.method}" for id = "{recipeID}"')
                abort(405)
        else:
            print(recipeID, recipes)
            abort(404)

@app.route('/recipe', methods = ['POST'])
def addRecipe() -> str:
    with RecipeDB(path) as recipes:
        try:
            data = request.get_json(force=True)
            r = Recipe.fromJson(data)
            recipes.addRecipe(r)
        except Exception as e:
            print(repr(e))
            raise
            #abort(500)
        return ''

@app.route('/allrecipes')
def listRecipes() -> str:
    with RecipeDB(path) as recipes:
        names = recipes.getNamesAndIDs()
        return jsonify(names)