
import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'sdgdfhgtr546yutjhgmfghkjmudsgerty546htj'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = '23refdhgyjt7iukyjhkmdgfgrt5657uyjhgmftre54y6uthgmj'
    JWT_ACCESS_TOKEN_EXPIRES = False
   
    
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:komolehin@localhost/sms"

class ProductionConfig(Config):
    DEBUG = True
    
class TestConfig(Config):
    DEBUG = True
    
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

config = {
    'development':DevelopmentConfig,
    'production':ProductionConfig,
    'default':DevelopmentConfig,
    'test':TestConfig
}