#/bin/bash

export FLASK_APP=flask_app.py
export FLASK_ENV=development

python -m flask run --host=0.0.0.0
