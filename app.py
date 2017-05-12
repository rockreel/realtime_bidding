import logging
import os
import sys

from flask import Flask
from flask_redis import FlaskRedis


app = Flask(__name__)
redis_store = FlaskRedis(app)

# Config app.
if os.getenv('ENV') == 'prod':
    app.config.from_object('config.ProductionConfig')
else:
    app.config.from_object('config.DevelopmentConfig')

# Setup logging.
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# Enable bidder or tracker routes depends on environment.
if os.getenv('APP') == 'bidder':
    import bidder
elif os.getenv('APP') == 'tracker':
    import tracker
else:
    import bidder
    import tracker


@app.errorhandler(Exception)
def handle_request(e):
    app.logger.exception(e)
    raise e


@app.route('/')
def index():
    return 'Realtime Bidding v0.1'