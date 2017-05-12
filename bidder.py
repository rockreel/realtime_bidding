from app import app
from app import redis_store


@app.route('/bid')
def bid():
    app.logger.info('bid')
    return 'bid'


@app.route('/win_notice')
def confirm():
    app.logger.info('win notice')
    return 'win notice'


@app.route('/error')
def error():
    raise Exception('Boo!')
