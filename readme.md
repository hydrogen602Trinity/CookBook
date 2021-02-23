
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

## Sqlite DB
Store data somehow?

add checkboxes

