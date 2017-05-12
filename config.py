import os


class Config(object):
    DEBUG = False
    TESTING = False
    REDIS_URL = 'redis://127.0.0.1'


class ProductionConfig(Config):
    REDIS_URL = os.getenv('REDIS_HOST')


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
