import json
import random
from urllib.parse import urlparse
from uuid import uuid4

import ad
from app import app
from app import redis_client


KEY_SPACE_BID = 'bid:'

PERSIST_SHORT_SECONDS = 60
PERSIST_LONG_SECONDS = 24 * 3600 * 3


def select_ads(bid_request):
    # The core bidding logic to match ads in inventory with impressions in the
    # request. Returns a list of (impression id, ad) to generate bid response.
    request_sizes = set(
        [(i['banner']['w'], i['banner']['h']) for i in bid_request['imp']])
    available_ads = filter(
        lambda a:
            (a.width, a.height) in request_sizes and
            ad.get_today_spend(a.id) < a.daily_budget,  # Still have budget.
        ad.get_ads()
    )

    imp_ad_list = []
    for imp in bid_request['imp']:
        fit_ads = list(filter(
            lambda x:
                x.width == imp['banner']['w'] and
                x.height == imp['banner']['h'],
            available_ads
        ))
        # Naive strategy to randomly select one from all eligible ads.
        if fit_ads:
            imp_ad_list.append((imp['id'], random.choice(fit_ads)))

    return imp_ad_list


def generate_response(bid_request):
    # Return generated bid id, bid response and selected ad ids.
    bid_id = str(uuid4())
    bids = []
    ad_ids = []
    for imp_id, ad in select_ads(bid_request):
        subbid_id = str(uuid4())
        ad_ids.append(ad.id)
        ad_markup = """
            <a href="%s">
                <img width="%s" height="%s" src="%s" alt=""/>
                <img src="%s" border="0" style="display: none;"/>
            </a>""" % (
                '%s?ad_id=%s&bid_id=%s&imp_id=%s' % (
                    app.config['CLICK_URL'], ad.id, bid_id, imp_id),
                ad.width,
                ad.height,
                ad.image_src,
                '%s?ad_id=%s&bid_id=%s&imp_id=%s' % (
                    app.config['IMPRESSION_URL'], ad.id, bid_id, imp_id),
                )

        bids.append(
            {
                'price': ad.cpm,
                'impid': imp_id,
                'id': subbid_id,
                'crid': ad.id,
                'cid': ad.id,
                'adm': ad_markup,
                'adomain': [urlparse(ad.dest_url).hostname],
                'nurl':
                    '%s?ad_id=%s&bid_id=%s&imp_id=%s&price=${AUCTION_PRICE}' % (
                        app.config['WIN_NOTICE_URL'], ad.id, bid_id, imp_id),
                'iurl': ad.image_src,
            }
        )
    if bids:
        bid_response = {
            'id': bid_request['id'],
            'bidid': bid_id,
            'seatbid': [
                {'bid': bids},
            ],
        }
    else:
        bid_response = {}
    return bid_id, bid_response, ad_ids


def persist_request(bid_id):
    # Persist stored bid longer for future collection.
    redis_client.expire(KEY_SPACE_BID + bid_id, PERSIST_LONG_SECONDS)


def store_request(bid_id, bid_request):
    # Store bid request for a short period.
    redis_client.hset(
        KEY_SPACE_BID + bid_id, 'request', json.dumps(bid_request))
    redis_client.expire(KEY_SPACE_BID + bid_id, PERSIST_SHORT_SECONDS)
    return bid_id


def store_response(bid_id, bid_response):
    # Store bid response.
    redis_client.hset(
        KEY_SPACE_BID + bid_id, 'response', json.dumps(bid_response))


def record_event(bid_id, imp_id, event):
    # Record given event in stored bid entry.
    redis_client.hset(KEY_SPACE_BID + bid_id, event + ':' + imp_id, 1)