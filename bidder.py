from app import app
from app import redis_store
from app import statsd_client


@app.route('/bid')
@statsd_client.timer('bidder.bid')
def bid():
    app.logger.info('bid')
    return 'bid'


@app.route('/win_notice')
@statsd_client.timer('bidder.win_notice')
def win_notice():
    app.logger.info('win notice')
    return 'win notice'


@app.route('/error')
def error():
    raise Exception('Boo!')
