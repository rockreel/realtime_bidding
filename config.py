import os


class Config(object):
    DEBUG = False
    TESTING = False
    REDIS_URL = 'redis://localhost'
    STATSD_URL = 'localhost'
    WIN_NOTICE_URL = 'http://localhost:5000/win_notice'
    CLICK_URL = 'http://localhost:5000/click'
    IMPRESSION_URL = 'http://localhost:5000/impression'


class ProductionConfig(Config):
    REDIS_URL = os.getenv('REDIS_URL')
    STATSD_URL = os.getenv('STATSD_URL')
    WIN_NOTICE_URL = os.getenv('WIN_NOTICE_URL')
    CLICK_URL = os.getenv('CLICK_URL')
    IMPRESSION_URL = os.getenv('IMPRESSION_URL')


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
