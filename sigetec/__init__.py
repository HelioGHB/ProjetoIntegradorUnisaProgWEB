from pathlib import Path

from flask import Flask, render_template

from config import Config


def create_app(test_config=None):
    app = Flask(__name__, template_folder='../templates')
    app.config.from_object(Config())
    if test_config:
        app.config.update(test_config)
    Path(app.instance_path).mkdir(exist_ok=True)

    @app.get('/')
    def inicio():
        return render_template('index.html')

    return app
