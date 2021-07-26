import os
basedir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig(object):
    DEBUG = True
    TESTING = False
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(basedir, 'carreseller.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(basedir, 'test.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'thisis the secret key' or os.environ.get('SECRET_KEY')


class TestingConfig(BaseConfig):
    Testing = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(  basedir, 'test.db' )
