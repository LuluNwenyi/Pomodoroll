###########################################
################ IMPORTS ##################
###########################################

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_manager
from .config import config, DevelopmentConfig, ProductionConfig
from flask_marshmallow import Marshmallow
from flask_mail import Mail
from datetime import timedelta


# TOKEN EXPIRY TIME
ACCESS_EXPIRES = timedelta(hours=24)

# APP CONFIG
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
mail = Mail(app)

# APP FACTORY
def create_app(config_name):

    # INIT APP CONFiG IN APP
    app.config.from_object(config[config_name])

    # INIT APP IN MANAGERS
    db.init_app(app)
    Migrate(app, db)
    ma.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    Bcrypt.init_app(Bcrypt, app=app)

    # REGISTRATION OF BLUEPRINTS
    from api.crud import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
