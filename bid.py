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


def select_ad(bid_request):
    # Naive strategy to randomly select an ad for bid response.
    return random.choice(ad.get_ads())


def generate_response(bid_request):
    # Return selected ad id, generated bid id and bid response.
    bid_id = str(uuid4())
    ad = select_ad(bid_request)
    ad_markup = """
        <a href="%s">
            <img width="%s" height="%s" src="%s" alt=""/>
            <img src="%s" border="0" style="display: none;"/>
        </a>""" % (
            '%s?ad_id=%s&bid_id=%s' % (
                app.config['CLICK_URL'], ad['id'], bid_id),
            ad['width'],
            ad['height'],
            ad['image_src'],
            '%s?ad_id=%s&bid_id=%s' % (
                app.config['IMPRESSION_URL'], ad['id'], bid_id),
            )

    bids = [
        {
            'price': float(ad['cpm']),
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
        }
    ]

    bid_response = {
        'id': bid_request['id'],
        'bidid': bid_id,
        'seatbid': [
            {'bid': bids},
        ],
    }
    return ad['id'], bid_id, bid_response


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


def record_event(bid_id, event):
    # Record given event in stored bid entry.
    redis_client.hset(KEY_SPACE_BID + bid_id, event, 1)