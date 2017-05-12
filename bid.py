import json
from urllib.parse import urlparse
from uuid import uuid4

from app import app
from app import redis_client


KEY_SPACE_BID = 'bid:'

PERSIST_SHORT_SECONDS = 60
PERSIST_LONG_SECONDS = 24 * 3600 * 3


def generate_response(ad, bid_request, bid_id):
    ad_markup = """
        <a href="%s">
            <img width="%d" height="%d" src="%s" alt=""/>
            <img src="%s" border="0" style="display: none;"/>
        </a>""" % (
            '%s?ad_id=%s&bid_id=%s' % (
                app.config['CLICK_URL'], ad['id'], bid_id),
            bid_request['imp'][0]['banner']['w'],
            bid_request['imp'][0]['banner']['h'],
            ad['image_src'],
            '%s?ad_id=%s&bid_id=%s' % (
                app.config['IMPRESSION_URL'], ad['id'], bid_id),
            )
    bid_array = [{
        'price': ad['cpm'],
        'impid': bid_request['imp'][0]['id'],
        'id': bid_id,
        'crid': ad['id'],
        'cid': ad['id'],
        'adm': ad_markup,
        'adomain': [urlparse(ad['dest_url']).hostname],
        'nurl':
            '%s?ad_id=%s&bid_id=%s&price=${AUCTION_PRICE}' % (
                app.config['WIN_NOTICE_URL'], ad['id'], bid_id),
        'iurl': ad['image_src'],
    }]

    bid = {
        'id': bid_request['id'],
        'bidid': bid_id,
        'seatbid': [{'bid': bid_array}],
    }
    return bid


def persist_request(bid_id):
    # Persist bid longer for future collection.
    redis_client.expire(KEY_SPACE_BID + bid_id, PERSIST_LONG_SECONDS)


def record_request(bid_request):
    # Record bid request.
    bid_id = str(uuid4())
    redis_client.hset(
        KEY_SPACE_BID + bid_id, 'request', json.dumps(bid_request))
    redis_client.expire(KEY_SPACE_BID + bid_id, PERSIST_SHORT_SECONDS)
    return bid_id


def record_event(bid_id, event):
    # Record given event in stored bid entry.
    redis_client.hset(KEY_SPACE_BID + bid_id, event, 1)