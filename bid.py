import json
from uuid import uuid4

from app import redis_client


KEY_SPACE_BID = 'bid:'

PERSIST_SHORT_SECONDS = 60
PERSIST_LONG_SECONDS = 24 * 3600 * 3


def persist(bid_id):
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