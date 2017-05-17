# Real-time Bidding

This is a simple real-time bidding system (advertising) implemented
using Python, Flask, Redis and Docker.

```
docker build -t rtb .
docker run -p 80:80 \
    -e "REDIS_URL=redis://$(ipconfig getifaddr en0)" \
    -e "STATSD_URL=$(ipconfig getifaddr en0)" \
    -e "WIN_NOTICE_URL=http://localhost/win_notice" \
    -e "CLICK_URL=http://localhost/click" \
    -e "IMPRESSION_URL=http://localhost/impression" \
    -e "ENV=dev"
    rtb
python client.py
```

Open http://localhost/ads/ to add and monitor ads.