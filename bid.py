import json
import random
from urllib import parse as urlparser
from uuid import uuid4

import ad
from app import app
from app import redis_client


KEY_SPACE_BID = 'bid:'

PERSIST_SHORT_SECONDS = 60
PERSIST_LONG_SECONDS = 24 * 3600 * 3


def select_ads(bid_request):
    # The core bidding logic to match ads in inventory with impressions in the
    # request. Return a list of (impression id, ad) to generate bid response.
    available_ads = [a for a in ad.get_ads() if a.is_available()]

    imp_ad_list = []
    for imp in bid_request['imp']:
        # Only bid on banner.
        if not imp.get('banner'):
            continue
        # Naive strategy to randomly select one from all eligible ads.
        selected_ads = [
            a for a in available_ads
            if a.width == imp['banner']['w'] and a.height == imp['banner']['h']]
        if selected_ads:
            imp_ad_list.append((imp['id'], random.choice(selected_ads)))

    return imp_ad_list


def generate_response(bid_request):
    # Return generated bid id, bid response and selected ad ids.
    bid_id = str(uuid4())
    bids = []
    ad_ids = []
    for imp_id, ad in select_ads(bid_request):
        ad_ids.append(ad.id)
        bids.append({
            'price': ad.cpm,
            'impid': imp_id,
            'id': str(uuid4()),
            'crid': ad.id,
            'cid': ad.id,
            'adm': get_ad_markup(ad, bid_id, imp_id),
            'adomain': [urlparser.urlparse(ad.dest_url).hostname],
            'nurl':
                get_url('WIN_NOTICE_URL',
                        ad.id, bid_id, imp_id, price='${AUCTION_PRICE}'),
            'iurl': ad.image_src,
        })
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


def get_url(url_type, ad_id, bid_id, imp_id, **kwargs):
    # Format various URLs in bid response and ad markup.
    params ={
        'ad_id': ad_id,
        'bid_id': bid_id,
        'imp_id': imp_id,
    }
    params.update(kwargs)
    return '%s?%s' % (
        app.config[url_type],
        '&'.join(['%s=%s' % (k, v) for k, v in params.items()]))


def get_ad_markup(ad, bid_id, imp_id):
    # Return ad markup for given ad.
    ad_markup = """
    <a href="%s">
        <img width="%s" height="%s" src="%s" alt=""/>
        <img src="%s" border="0" style="display: none;"/>
    </a>""" % (
        get_url('CLICK_URL', ad.id, bid_id, imp_id),
        ad.width,
        ad.height,
        ad.image_src,
        get_url('IMPRESSION_URL', ad.id, bid_id, imp_id),
    )
    return ad_markup


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