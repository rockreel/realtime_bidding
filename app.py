import logging
import os

from flask import Flask
from flask_redis import FlaskRedis
import statsd


app = Flask(__name__)

# Config app.
if os.getenv('ENV') == 'prod':
    app.config.from_object('config.ProductionConfig')
else:
    app.config.from_object('config.DevelopmentConfig')

# Setup external services.
redis_client = FlaskRedis(app, charset='utf-8', decode_responses=True)
statsd_client = statsd.StatsClient(app.config['STATSD_URL'])

# Setup logging to log to console, so that it can be easily collected from
# docker.
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


# Common routes and setups.
@app.errorhandler(Exception)
def handle_request(e):
    statsd_client.incr('%s.error' % os.getenv('APP', 'bidder'))
    app.logger.exception(e)
    raise e


@app.route('/')
def index():
    return 'Realtime Bidding v0.1'
