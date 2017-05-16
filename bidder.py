from flask import jsonify
from flask import request
from flask import make_response

import ad
from app import app
from app import statsd_client
import bid


@app.route('/bid', methods=['POST'])
@statsd_client.timer('bidder.bid')
def bid_():
    bid_request = request.json
    ad_id, bid_id, bid_response = bid.generate_response(bid_request)
    ad.incr_report(ad_id, 'bids', 1)
    bid.store_request(bid_id, bid_request)
    bid.store_response(bid_id, bid_response)
    return jsonify(bid_response)


@app.route('/win_notice', methods=['GET'])
@statsd_client.timer('bidder.win_notice')
def win_notice():
    bid.persist_request(request.args['bid_id'])
    ad.incr_report(request.args['ad_id'], 'wons', 1)
    ad.incr_report(request.args['ad_id'], 'spend', float(request.args['price']))
    return make_response('', 200)

