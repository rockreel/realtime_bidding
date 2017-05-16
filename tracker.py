from flask import request
from flask import redirect
from flask import make_response

import ad
from app import app
from app import statsd_client
import bid


@app.route('/impression', methods=['GET'])
@statsd_client.timer('tracker.impression')
def impression():
    bid_id = request.args['bid_id']
    bid.record_event(bid_id, 'impression')
    ad_id = request.args['ad_id']
    ad.incr_report(ad_id, 'impressions', 1)
    return make_response('', 200)


@app.route('/click', methods=['GET'])
@statsd_client.timer('tracker.click')
def click():
    bid_id = request.args['bid_id']
    bid.record_event(bid_id, 'click')
    ad_id = request.args['ad_id']
    ad.incr_report(ad_id, 'clicks', 1)
    return make_response(redirect(ad.get_ad(ad_id)['dest_url']))

