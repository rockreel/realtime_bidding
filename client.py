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
parser.add_argument('-i', '--interval', dest='interval',
                    type=int, default=1,
                    help='Interval second to send request.')
args = parser.parse_args()


def process_bid(bid):
    imp_id = bid['impid']
    price = bid['price']
    print('Impression %s' % imp_id)
    print('Price: $%s' % price)
    soup = BeautifulSoup(bid['adm'], 'html.parser')
    print('Ad Markup:\n%s' % soup.prettify())

    # Mock auction won.
    if random.random() < args.win_rate:
        print('Auction won!')
        nurl = bid['nurl'].replace('${AUCTION_PRICE}', str(price))
        print('Ping win notice: %s' % nurl)
        requests.get(nurl)
        for img in soup.find_all('img'):
            print('Ping image: %s' % img['src'])
            requests.get(img['src'])

        # Mock ad click.
        if random.random() < args.click_through_rate:
            print('User click!')
            for a in soup.find_all('a'):
                print('Click: %s' % a['href'])
                requests.get(a['href'])


def main():
    with open(args.request_file) as f:
        for line in f:
            print('Send bid request to %s' % args.bidder_url)
            st = time.time()
            response = requests.post(
                args.bidder_url, json=json.loads(line))
            print('Latency: %s ms' % ((time.time() - st)*1000))
            if response.status_code == 204:
                print('No bids.\n\n')
            else:
                print('Process bids:')
                for bid in response.json()['seatbid'][0]['bid']:
                    process_bid(bid)
                print('\n\n')

            time.sleep(args.interval)


if __name__ == '__main__':
    main()