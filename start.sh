#/bin/bash

if [[ $1 == "test" ]]
then
    export INIT_DB=0
    export DB_FILENAME=test.db
    export TESTING=1
else
    if [[ $1 == "init" ]]
    then
        export INIT_DB=1    
    else
        export INIT_DB=0
    fi
    export DB_FILENAME=prod.db
fi

export FLASK_APP=flask_app.py
export FLASK_ENV=development

if [[ $1 == "test" ]]
then
    python -m unittest --locals
else
    python -m flask run --host=0.0.0.0
fi