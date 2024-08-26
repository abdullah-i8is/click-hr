import os
from sqlalchemy import create_engine
class Config(object):

    basedir = os.path.abspath(os.path.dirname(__file__))

    # Set up the App SECRET_KEY
    SECRET_KEY = os.getenv('SECRET_KEY', 'Geoxhr123??')

    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://hayat:Hayat_admin123@35.183.134.169/geoxhrdb'
    
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://hayat:Hayat_admin123@3.99.155.18/clickhrdemo'

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://hayat:Hayat_admin123@35.183.134.169/Clickhrin'

    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/clickhrinfiniti'



    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 30
    SQLALCHEMY_POOL_TIMEOUT = 60
    SQLALCHEMY_POOL_RECYCLE = 3600

    # Assets Management
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', 'app/static')



#
class ProductionConfig(Config):
    DEBUG = False

    # Security
    # SESSION_COOKIE_HTTPONLY = True
    # REMEMBER_COOKIE_HTTPONLY = True
    # REMEMBER_COOKIE_DURATION = 3600



# PostgreSQL database
    # SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
    #     os.getenv('DB_ENGINE'   , 'mysql'),
    #     os.getenv('DB_USERNAME' , 'hayat'),
    #     os.getenv('DB_PASS'     , 'Hayat_admin123'),
    #     os.getenv('DB_HOST'     , '3.99.155.18'),
    #     os.getenv('DB_PORT'     , 3306),
    #     os.getenv('DB_NAME'     , 'geoxhrdb')
#     SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
#                 os.getenv('DB_ENGINE'   , 'mysql'),
#                 os.getenv('DB_USERNAME' , 'hayat'),
#                 os.getenv('DB_PASS'     , 'Hayat_admin123'),
#                 os.getenv('DB_HOST'     , '3.99.155.18'),
#                 os.getenv('DB_PORT'     , 3306),
#                 os.getenv('DB_NAME'     , 'clickhrdemo')

    SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
        os.getenv('DB_ENGINE'   , 'mysql'),
        os.getenv('DB_USERNAME' , 'hayat'),
        os.getenv('DB_PASS'     , 'Hayat_admin123'),
        os.getenv('DB_HOST'     , '35.183.134.169'),
        os.getenv('DB_PORT'     , 3306),
        os.getenv('DB_NAME'     , 'Clickhrin')

    )
#     )

class DebugConfig(Config):
    DEBUG = True


# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug'     : DebugConfig
}
