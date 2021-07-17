from flask import render_template, Blueprint, render_template, send_from_directory

core = Blueprint(
                 __name__.split('.', maxsplit=1)[1], 
                 __name__,
                 template_folder='../templates'
                )


@core.route('/')
def hello_world():
    return render_template("main.html")

@core.route('/assets/<path:path>')
def send_js(path):
    return send_from_directory('assets', path)
