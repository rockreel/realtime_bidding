import argparse
import json
import random
import requests
import time

from bs4 import BeautifulSoup


parser = argparse.ArgumentParser(description='Realtime Bidding Test Client')
parser.add_argument('-b', '--bidder_url', dest='bidder_url', type=str,
                    default='http://localhost:5000/bid',
                    help='Bidder URL.')
parser.add_argument('-r', '--request_file', dest='request_file', type=str,
                    default='requests.json',
                    help='Test request file.')
parser.add_argument('-c', '--click_through_rate', dest='click_through_rate',
                    type=float, default=0.5,
                    help='Click through rate to mock user click.')
parser.add_argument('-w', '--win_rate', dest='win_rate',
                    type=float, default=0.5,
                    help='Win rate to mock exchange auction win.')


def main():
    args = parser.parse_args()
    with open(args.request_file) as f:
        for line in f:
            st = time.time()
            response = requests.post(
                args.bidder_url, json=json.loads(line)).json()
            print('Latency: %s ms' % ((time.time() - st)*1000))
            price = response['seatbid'][0]['bid'][0]['price']
            ad_markup = response['seatbid'][0]['bid'][0]['adm']
            soup = BeautifulSoup(ad_markup, 'html.parser')
            print('Ad Markup:\n %s' % soup.prettify())

            # Won an auction, call win notice and load images.
            if random.random() < args.win_rate:
                nurl = response['seatbid'][0]['bid'][0]['nurl']
                nurl = nurl.replace('${AUCTION_PRICE}', str(price / 1000.0))
                print('Ping win notice: %s' % nurl )
                requests.get(nurl)
                for img in soup.find_all('img'):
                    print('Ping image: %s' % img['src'])
                    requests.get(img['src'])

                # Click an ad.
                if random.random() < args.click_through_rate:
                    for a in soup.find_all('a'):
                        print('Click: %s' % a['href'])
                        requests.get(a['href'])

            time.sleep(3)


if __name__ == '__main__':
    main()