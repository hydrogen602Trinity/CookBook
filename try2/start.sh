#/bin/bash

if [[ $1 == "init" ]]
then
    export INIT_DB=1
else
    export INIT_DB=0
fi


export FLASK_APP=flask_app.py
export FLASK_ENV=development

python -m flask run --host=0.0.0.0
