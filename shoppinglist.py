from fractions import Fraction
from typing import Optional
from flask import request
from flask.json import jsonify
from flask_restful import Resource, Api, reqparse
from flask import Blueprint
from flask_login import current_user
from datetime import date
from math import ceil
from typing import List

from models import Ingredient, Recipe, db, User, Meal, Tag
from restapi.auth_util import require_admin, require_auth

def sortIngredients(i: Ingredient) -> str:
    return i.name

# List of Ingredient Amounts:
# None
# Teaspoon (tsp)
# Tablespoon (tbsp)
# Cup
# Ounces (oz)
# Pounds (lb)
# Others

def combineIngredients(name: str, ing1: Ingredient, ing2: Ingredient) -> Ingredient:

    amt1 = ing1.amount
    amt2 = ing2.amount
    unit1 = ing1.unit
    unit2 = ing2.unit

    # Convert to Mililiters
    ml1 = False
    if unit1 == "ml":
        ml1 = True
    elif unit1 == "cup":
        amt1 *= 237
        ml1 = True
    elif unit1 == "tbsp":
        amt1 *= 15
        ml1 = True
    elif unit1 == "tsp":
        amt1 *= 5
        ml1 = True

    ml2 = False
    if unit1 == "ml":
        ml2 = True
    elif unit2 == "cup":
        amt2 *= 237
        ml2 = True
    elif unit2 == "tbsp":
        amt2 *= 15
        ml2 = True
    elif unit2 == "tsp":
        amt2 *= 5
        ml2 = True
    
    if unit1 == "lb" and unit2 == "lb":
        return Ingredient(name, ceil(amt1+amt2), "lb")
    elif ml1 and ml2:
        return Ingredient(name, ceil(amt1+amt2), "ml")
    else:
        raise ValueError(f"Error - Unable to combine ingredients of type {unit1} and {unit2}")

def create_shoppinglist(meals: List[Meal]) -> List[Ingredient]:

    shopList = []
    # Note: Figure out the dark sorcery behind tablespoons and teaspoons
    for meal in meals:
        recipe: Optional[Recipe] = db.session.query(Recipe).filter(meal.recipe_id == Recipe.id).one_or_none()
        if recipe:
            print(recipe.name)
            for ingredient in recipe.ingredients:
                shopList.append(ingredient)

    shopList.sort(key = sortIngredients)

    # Search for Ingredients with the Same Name
    prev = Ingredient("", 0)
    for item in shopList.copy():
        if item.name == prev.name:
            newItem = combineIngredients(item.name, item, prev)
            item.amount = newItem.amount
            item.unit = newItem.unit
            shopList.remove(prev)
        prev = item

    return shopList