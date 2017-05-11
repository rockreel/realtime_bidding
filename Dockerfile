FROM ubuntu

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get install -y python python-pip nginx gunicorn supervisor

# Setup flask application
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt

# Setup nginx
RUN rm /etc/nginx/sites-enabled/default
COPY conf/flask.conf /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/flask.conf /etc/nginx/sites-enabled/flask.conf
RUN echo "daemon off;" >> /etc/nginx/nginx.conf

# Setup supervisord
RUN mkdir -p /var/log/supervisor
COPY conf/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80

# Start processes
CMD ["/usr/bin/supervisord"]