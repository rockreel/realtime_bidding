import os

from flask import Flask
app = Flask(__name__)


if os.getenv('APP') == 'bidder':
    import bidder
elif os.getenv('APP') == 'tracker':
    import tracker
else:
    import bidder
    import tracker