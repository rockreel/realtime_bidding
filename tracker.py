from datetime import datetime

from flask import request
from flask import redirect
from flask import make_response

import ad
from app import app
from app import redis_client
from app import statsd_client
import bid


@app.route('/impression')
@statsd_client.timer('tracker.impression')
def impression():
    bid.record_event(request.args['bid_id'], 'impression')
    ad.incr_report(request.args['ad_id'], 'impressions', 1)
    return make_response('', 200)


@app.route('/click')
@statsd_client.timer('tracker.click')
def click():
    bid.record_event(request.args['bid_id'], 'click')
    ad.incr_report(request.args['ad_id'], 'clicks', 1)
    return make_response(redirect(ad.get_dest_url(request.args['ad_id'])))

