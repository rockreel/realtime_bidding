from app import app


@app.route('/')
def index():
    return 'Realtime Bidding V1'


@app.route('/bid')
def bid():
    return 'bid'


@app.route('/confirm')
def confirm():
    return 'confirm'
