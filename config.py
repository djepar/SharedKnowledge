# config.py
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'classroom.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CSS_MINIFY = False    
class DevelopmentConfig(Config):
    DEBUG = True
    CSS_MINIFY = False
class ProductionConfig(Config):
    DEBUG = False
    CSS_MINIFY = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
