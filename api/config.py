#----- IMPORTS -----#

import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

basedir = os.path.abspath(os.path.dirname(__file__))

# BASE CONFIG
class Config():

    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get('SENDGRID_API_KEY')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')

    @staticmethod
    def init_app():
        pass


# DEVELOPMENT CONFIG
class DevelopmentConfig(Config):

    DEBUG = True 
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    

# TESTING CONFIG
class TestingConfig(Config):

    TESTING = True 
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")


# PRODUCTION CONFIG
class ProductionConfig(Config):

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", -1)


#ENV CONFiG
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}