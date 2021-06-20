from flask import render_template

from flask import Blueprint, render_template, abort

core = Blueprint(
                 __name__.split('.', maxsplit=1)[1], 
                 __name__,
                 template_folder='../templates'
                )


@core.route('/')
def hello_world():
    return render_template("main.html")
