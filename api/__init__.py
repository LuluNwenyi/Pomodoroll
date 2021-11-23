#----- IMPORTS -----#

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from .config import config
from flask_mail import Mail
from datetime import timedelta
from flask_cors import CORS

# TOKEN EXPIRY TIME
ACCESS_EXPIRES = timedelta(hours=24)

# APP CONFIG
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
jwt = JWTManager()
mail = Mail()
cors = CORS()

# APP FACTORY
def create_app(config_name):

    # INIT APP CONFiG IN APP
    app.config.from_object(config[config_name])

    # INIT APP IN MANAGERS
    db.init_app(app)
    Migrate(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    Bcrypt.init_app(Bcrypt, app=app)
    cors.init_app(app)

    # REGISTRATION OF BLUEPRINTS
    from api.crud import default as default_blueprint
    from api.auth.routes import auth as auth_blueprint
    from api.user.routes import user as user_blueprint
    from api.admin.routes import admin as admin_blueprint
    from api.task.routes import task as task_blueprint
    from api.pomodoro.routes import timer as pomodoro_blueprint
    
    app.register_blueprint(default_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(pomodoro_blueprint)
    app.register_blueprint(task_blueprint)

    return app
