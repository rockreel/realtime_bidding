from datetime import datetime

from app import redis_client

KEY_SPACE_AD = 'ad:'
KEY_SPACE_REPORT = 'report:'

REPORT_PERSIST_DAYS = 30


def get_dest_url(ad_id):
    # Return destination url for given ad id.
    return redis_client.hget(KEY_SPACE_AD + ad_id, 'dest_url')


def incr_report(ad_id, field, amount):
    # Increase ad report for given ad id and field.
    ad_key = KEY_SPACE_AD + ad_id
    today = datetime.utcnow().date().isoformat()
    report_key = KEY_SPACE_REPORT + '%s:%s' % (ad_id, today)

    if redis_client.hsetnx(report_key, 'date', today):
        redis_client.expire(report_key, 3600 * 24 * REPORT_PERSIST_DAYS)

    if type(amount) == float:
        redis_client.hincrbyfloat(ad_key, field, amount)
        redis_client.hincrbyfloat(report_key, field, amount)
    elif type(amount) == int:
        redis_client.hincrby(ad_key, field, amount)
        redis_client.hincrby(report_key, field, amount)
    else:
        raise Exception('Not support type %s to increase perf' % type(amount))

    return
