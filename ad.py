from datetime import datetime

from app import redis_client

KEY_SPACE_AD = 'ad:'
KEY_SPACE_REPORT = 'report:'


class Ad(object):
    # Wrapper around ad stored in Redis as hash.
    def __init__(self, ad_dict):
        self.id = int(ad_dict['id'])
        self.dest_url = ad_dict['dest_url']
        self.image_src = ad_dict['image_src']
        self.width = int(ad_dict['width'])
        self.height = int(ad_dict['height'])
        self.cpm = float(ad_dict['cpm'])
        self.daily_budget = float(ad_dict['daily_budget'])
        self.spend = float(ad_dict.get('spend', 0))
        self.bids = int(ad_dict.get('bids', 0))
        self.wons = int(ad_dict.get('wons', 0))
        self.impressions = int(ad_dict.get('impressions', 0))
        self.clicks = int(ad_dict.get('clicks', 0))


def get_ads():
    return [
        Ad(redis_client.hgetall(KEY_SPACE_AD + ad_id))
        for ad_id in redis_client.smembers('ad_ids')]


def get_ad(ad_id):
    ad_dict = redis_client.hgetall(KEY_SPACE_AD + str(ad_id))
    return Ad(ad_dict) if ad_dict else None


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


def delete_ad(ad_id):
    pipe = redis_client.pipeline(transaction=True)
    pipe.delete(KEY_SPACE_AD + str(ad_id))
    pipe.srem('ad_ids', ad_id)
    pipe.execute()
    return


def get_today_spend(ad_id):
    today = datetime.utcnow().date().isoformat()
    return float(
        redis_client.hget(KEY_SPACE_REPORT + '%s:%s' % (ad_id, today), 'spend')
        or 0.0)


def incr_report(ad_id, field, amount):
    # Increase ad report for given ad id and field.
    ad_key = KEY_SPACE_AD + str(ad_id)
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
