
# Plan

do we have one?  
how do we deal with units?  

## Data:
- Recipe
    - Ingredients (`?`)
        - `Dict[str, int]` units?
        - `Dict[str, (int, str)]` with units as str? maybe enum?
    - Instructions (`List[str]`) if steps
    - Notes (`str`)
    - Id (`str`) name based or random?
        - has to be url safe
    - Name (`str`)

## REST API
- add recipe (`POST`) 
    - `POST ... /recipe`
- get recipe (`GET`)
    - `GET ... /recipe/{id}`
- list recipes (`GET`)
    - `GET ... /allrecipes`
- delete recipe (`DELETE`)
    - `DELETE ... /recipe/{id}`
- update recipe (`PUT`)
    - `PUT ... /recipe/{id}`

## JSON Layout (Example)

```
{
    "recipeName": "Omelette", 
    "ingredients": [
        {
            "name": "Eggs", 
            "unit": "", 
            "amount": "2"
        }, 
        {
            "name": "Mozzarella", 
            "unit": "handful", 
            "amount": "1"
        }, 
        {
            "name": "Salt", 
            "unit": "teaspoon", 
            "amount": "1"
        }
    ], 
    "instructions": [
        "Break and beat eggs with fork", 
        "add salt", 
        "let cook in a pan", 
        "add cheese and fold"
    ], 
    "notes": "Don't turn the stove up too much", 
    "id": "UHBq23riRNmgopmBDHi1OQ=="
}
```

## Sqlite DB
Store data somehow?

add checkboxes

