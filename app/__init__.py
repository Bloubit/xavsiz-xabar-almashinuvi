from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from flask_bcrypt import Bcrypt

from flask_login import LoginManager


db = SQLAlchemy()

bcrypt = Bcrypt()

login_manager = LoginManager()


def create_app():

    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'super_secret_key'

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'postgresql://macbookuz@localhost/secure_messaging_db'
    )

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['SESSION_COOKIE_SECURE'] = True

    app.config['REMEMBER_COOKIE_SECURE'] = True

    app.config['SESSION_COOKIE_HTTPONLY'] = True

    db.init_app(app)

    bcrypt.init_app(app)

    login_manager.init_app(app)

    login_manager.login_view = 'main.login'

    from app.routes import main

    app.register_blueprint(main)

    with app.app_context():

        from app.models import (
            User,
            Message
        )

        db.create_all()

    return app