from flask.json import jsonify
from recipedb import RecipeDB
from flask import Flask, abort, request
import recipe
import os

app = Flask(__name__)

# tempRecipe = recipe.Recipe("Chocolate Milk", [
#     recipe.Ingredient("Milk", "cup", 1), 
#     recipe.Ingredient("Chocolate", "teaspoon", 2)], ["Add chocolate to milk", "Stir"], "Can add more chocolate if desired")
#recipes: Dict[str, recipe.Recipe] = { tempRecipe.id: tempRecipe } # temporary

path: str = ':memory:'
if 'DATABASE_PATH' in os.environ:
    path = os.environ['DATABASE_PATH']

recipes: RecipeDB = RecipeDB(path)

# recipes.addRecipe(tempRecipe)
# print(tempRecipe.id)

@app.route('/')
def hello_world():
    with open('frontend/test.html') as f:
        return f.read()

@app.route('/recipe/<string:recipeID>', methods = ['GET', 'DELETE'])
def getRecipe(recipeID: str) -> str:
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
    try:
        data = request.get_json(force=True)
        r = recipe.Recipe.fromJson(data)
        recipes.addRecipe(r)
    except Exception as e:
        print(repr(e))
        raise
        #abort(500)
    return ''

@app.route('/allrecipes')
def listRecipes() -> str:
    names = list(recipes.getNames())
    return jsonify(names)