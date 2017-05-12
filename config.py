import os


class Config(object):
    DEBUG = False
    TESTING = False
    REDIS_URL = 'redis://localhost'
    STATSD_URL = 'localhost'


class ProductionConfig(Config):
    REDIS_URL = os.getenv('REDIS_URL')
    STATSD_URL = os.getenv('STATSD_URL')


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
