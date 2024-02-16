#!/bin/sh

# This script is meant to be invoked via runit (installed in /etc/service/nginx/run), not directly

uwsgi --plugin python3 \
      --uid 33 \
      --master \
      --socket "127.0.0.1:8888" \
      --wsgi-file /etc/asrservice.wsgi \
      --processes ${UWSGI_PROCESSES:-2} \
      --threads ${UWSGI_THREADS:-2} \
      --env HOME=/var/www \
      --manage-script-name

