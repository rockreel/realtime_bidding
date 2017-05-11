from app import app


@app.route('/impression')
def impression():
    return 'impression'


@app.route('/click')
def click():
    return 'click'