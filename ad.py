from datetime import datetime

from app import redis_client

KEY_SPACE_AD = 'ad:'
KEY_SPACE_REPORT = 'report:'


class Ad(object):
    # Wrapper around ad object stored in Redis as hash. Mainly for type
    # conversion and sanity check.
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

    @property
    def spend_today(self):
        report_key = KEY_SPACE_REPORT + '%s:%s' % (
            self.id, datetime.utcnow().date().isoformat())
        return float(redis_client.hget(report_key, 'spend') or 0)

    def is_available(self):
        # If ad is available for bidding.
        return self.spend_today < self.daily_budget


def get_ads():
    return [
        Ad(redis_client.hgetall(KEY_SPACE_AD + ad_id))
        for ad_id in redis_client.smembers('ad_ids')]


def get_ad(ad_id):
    ad_dict = redis_client.hgetall(KEY_SPACE_AD + str(ad_id))
    return Ad(ad_dict) if ad_dict else None


def create_ad(dest_url, image_src, width, height, cpm, daily_budget):
    return _create_or_update_ad(
        None, dest_url, image_src, width, height, cpm, daily_budget)


def update_ad(ad_id, **kwargs):
    return _create_or_update_ad(ad_id, **kwargs)


def _create_or_update_ad(ad_id, dest_url, image_src, width, height, cpm,
                         daily_budget):
    ad = {}
    if dest_url is not None:
        ad['dest_url'] = dest_url
    if image_src is not None:
        ad['image_src'] = image_src
    if width is not None:
        ad['width'] = int(width)
    if height is not None:
        ad['height'] = int(height)
    if cpm is not None:
        ad['cpm'] = float(cpm)
    if daily_budget is not None:
        ad['daily_budget'] = float(daily_budget)
    if ad_id is None:
        ad_id = redis_client.incr('ad_id_seq')
    ad['id'] = int(ad_id)

    pipe = redis_client.pipeline(transaction=True)
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


def incr_report(ad_id, field, amount):
    # Increase ad report for given ad id and field.
    ad_key = KEY_SPACE_AD + str(ad_id)
    today = datetime.utcnow().date().isoformat()
    report_key = KEY_SPACE_REPORT + '%s:%s' % (ad_id, today)

    pipe = redis_client.pipeline(transaction=True)
    if type(amount) == float:
        pipe.hincrbyfloat(ad_key, field, amount)
        pipe.hincrbyfloat(report_key, field, amount)
    elif type(amount) == int:
        redis_client.hincrby(ad_key, field, amount)
        redis_client.hincrby(report_key, field, amount)
    else:
        raise Exception('Not support type %s' % type(amount))
    pipe.execute()

    return
