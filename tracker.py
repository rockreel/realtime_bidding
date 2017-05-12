from app import app
from app import redis_store


@app.route('/impression')
def impression():
    return 'impression'


@app.route('/click')
def click():
    return 'click'
