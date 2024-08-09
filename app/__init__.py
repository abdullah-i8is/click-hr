from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = 'Geoxhr123??'
app.config.from_object(Config)

db = SQLAlchemy()
login_manager = LoginManager()

from app import routes, model

db.init_app(app)
login_manager.init_app(app)

def register_extensions(app):
    login_manager.init_app(app)

def configure_database(app):

    with app.app_context():
        db.create_all()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

def create_app(config):
    app.config.from_object(config)
    register_extensions(app)
    configure_database(app)
    return app

if __name__ == '__main__':
    app.run(debug=True)
