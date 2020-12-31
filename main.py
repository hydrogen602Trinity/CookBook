from flask import Flask, abort
app = Flask(__name__)

import recipe
from typing import Dict
import fractions 

tempRecipe = recipe.Recipe("Chocolate Milk", [
    recipe.Ingredient("Milk", "cup", fractions.Fraction(1)), 
    recipe.Ingredient("Chocolate", "spoon", fractions.Fraction(2))], ["Add chocolate to milk", "Stir"], "Can add more chocolate if desired")
recipes: Dict[str, recipe.Recipe] = { tempRecipe.id: tempRecipe } # temporary

print(tempRecipe.id)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/recipe/<string:recipeID>')
def getRecipe(recipeID: str) -> str:
    if recipeID in recipes:
        return recipes[recipeID].toJson()
    else:
        print(recipeID, recipes)
        abort(404)