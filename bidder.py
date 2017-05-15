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
    bid_id = bid.record_request(bid_request)
    ad_id = next(iter(ad.get_active_ad_ids()))
    ad_ = ad.get_ad_by_id(ad_id)
    ad.incr_report(ad_id, 'bids', 1)
    bid_response = bid.generate_response(ad_, bid_request, bid_id)
    bid.record_response(bid_response)
    return jsonify(bid_response)


@app.route('/win_notice', methods=['GET'])
@statsd_client.timer('bidder.win_notice')
def win_notice():
    bid.persist_request(request.args['bid_id'])
    ad.incr_report(request.args['ad_id'], 'bid_successes', 1)
    ad.incr_report(request.args['ad_id'], 'spend', float(request.args['price']))
    return make_response('', 200)

