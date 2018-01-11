
class Config(object):
    DEBUG = False

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'Passw0rd'
    MYSQL_DB = 'test'
    MYSQL_CURSORCLASS = 'DictCursor'

class TestingConfig(Config):
    TESTING = True

# email server
MAIL_SERVER = 'your.mailserver.com'
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_USERNAME = None
MAIL_PASSWORD = None

# administrator list
ADMINS = ['your-gmail-username@gmail.com']