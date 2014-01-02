# You should rename this file to config.py and change the mongodb
# details as required

class _Config(object):
    DEBUG = True
    TESTING = True
    HOST = '0.0.0.0'
    PORT = 5000
    MONGO_HOST = 'localhost'
    MONGO_PORT = 27019
    MONGO_USER = ''
    MONGO_PASS = ''
    DB_NAME = 'autobenchmark'
    ADMINEMAIL = 'youruser@yourdomain.com'
    HELPPAGE = 'http://github.com/minid33/autobenchmarkui'
    FAQPAGE = 'http://faq/'


class ProductionConfig(_Config):
    cfgname = 'prod'
    #DEBUG = False
    #TESTING = False


class DevelopmentConfig(_Config):
    cfgname = 'dev'


class TestingConfig(_Config):
    cfgname = 'test'
    MONGO_HOST = 'localhost'
    MONGO_PORT = 14234
    MONGO_USER = None
    MONGO_PASS = None
    DB_NAME = 'test'


Configs = {cls.cfgname: cls for cls in
           [ProductionConfig, DevelopmentConfig, TestingConfig]}
