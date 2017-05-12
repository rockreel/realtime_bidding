import json
import requests
import time


def main():
    with open('requests.json') as f:
        for line in f:
            r = requests.post(
                'http://127.0.0.1:5000/bid', json=json.loads(line))
            bid_response = r.json()
            ad_markup = bid_response['seatbid'][0]['bid'][0]['adm']
            print(ad_markup)
            with open('ad_markup.html', 'w') as f1:
                f1.write(ad_markup)
            win_notice_url = bid_response['seatbid'][0]['bid'][0]['nurl'].replace('${AUCTION_PRICE}', '1.0')
            print('Win notice: %s' % win_notice_url )
            requests.get(win_notice_url)
            time.sleep(5)

if __name__ == '__main__':
    main()