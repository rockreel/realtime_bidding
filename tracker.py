from app import app
from app import redis_store
from app import statsd_client


@app.route('/impression')
@statsd_client.timer('tracker.impression')
def impression():
    return 'impression'


@app.route('/click')
@statsd_client.timer('tracker.click')
def click():
    return 'click'
