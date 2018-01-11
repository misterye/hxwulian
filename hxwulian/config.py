class Config(object):
    DEBUG = False

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'Passw0rd'
    MYSQL_DB = 'hxwulian'
    MYSQL_CURSORCLASS = 'DictCursor'

class TestingConfig(Config):
    TESTING = True
