import fractions
import json
import sys, os
sys.path.append(os.path.join(sys.path[0], '..'))

import recipe

def test_ingredient():
    i = recipe.Ingredient('spam', 'can', fractions.Fraction(1, 2))

    assert i.toJsonSerializable() == {'name': 'spam', 'unit': 'can', 'amount': '1/2'}
    assert json.dumps(i.toJsonSerializable()) == '{"name": "spam", "unit": "can", "amount": "1/2"}'
    
    x = json.dumps(i.toJsonSerializable())

    i2 = recipe.Ingredient.fromJson(x)

    assert i2.amount == i.amount
    assert i2.name == i.name
    assert i2.unit == i.unit