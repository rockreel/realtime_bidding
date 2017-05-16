from datetime import datetime

from app import redis_client

KEY_SPACE_AD = 'ad:'
KEY_SPACE_REPORT = 'report:'


def get_ads():
    return [
        redis_client.hgetall(KEY_SPACE_AD + ad_id)
        for ad_id in redis_client.smembers('ad_ids')]


def get_ad_by_id(ad_id):
    return redis_client.hgetall(KEY_SPACE_AD + str(ad_id))


def create_or_update_ad(ad_id, dest_url, image_src, width, height, cpm,
                        daily_budget):
    if not ad_id:
        ad_id = redis_client.incr('ad_id_seq')
    pipe = redis_client.pipeline(transaction=True)
    ad = {
        'id': ad_id,
        'dest_url': dest_url,
        'image_src': image_src,
        'width': width,
        'height': height,
        'cpm': cpm,
        'daily_budget': daily_budget,
    }
    pipe.hmset(KEY_SPACE_AD + str(ad_id), ad)
    pipe.sadd('ad_ids', ad_id)
    pipe.execute()
    return ad_id


def remove_ad(ad_id):
    pipe = redis_client.pipeline(transaction=True)
    pipe.rem(KEY_SPACE_AD + str(ad_id))
    pipe.srem('ad_ids', ad_id)
    pipe.execute()
    return


def get_dest_url(ad_id):
    # Return destination url for given ad id.
    return redis_client.hget(KEY_SPACE_AD + ad_id, 'dest_url')


def incr_report(ad_id, field, amount):
    # Increase ad report for given ad id and field.
    ad_key = KEY_SPACE_AD + ad_id
    today = datetime.utcnow().date().isoformat()
    report_key = KEY_SPACE_REPORT + '%s:%s' % (ad_id, today)

    if type(amount) == float:
        redis_client.hincrbyfloat(ad_key, field, amount)
        redis_client.hincrbyfloat(report_key, field, amount)
    elif type(amount) == int:
        redis_client.hincrby(ad_key, field, amount)
        redis_client.hincrby(report_key, field, amount)
    else:
        raise Exception('Not support type %s' % type(amount))

    return
