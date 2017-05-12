from flask import request
from flask import make_response

import ad
from app import app
from app import statsd_client
import bid


@app.route('/bid')
@statsd_client.timer('bidder.bid')
def bid_():
    bid_request = request.json
    bid.record_request(bid_request)
    return make_response('', 200)


@app.route('/win_notice')
@statsd_client.timer('bidder.win_notice')
def win_notice():
    bid.persist(request.args['bid_uuid'])
    ad.incr_report(request.args['ad_id'], 'bid_successes', 1)
    ad.incr_report(request.args['ad_id'], 'spend', float(request.args['price']))
    return make_response('', 200)

