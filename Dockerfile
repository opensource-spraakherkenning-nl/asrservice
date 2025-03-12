FROM nvidia/cuda:12.6.3-base-ubuntu24.04

LABEL org.opencontainers.image.authors="Maarten van Gompel <proycon@anaproy.nl>"
LABEL description="An Automatic Speech Recognition webservice powered by WhisperX (ASR) and CLAM (webservice)" 

ENV UWSGI_PROCESSES=2
ENV UWSGI_THREADS=2

# By default, there is no authentication on the service,
# which is most likely not what you want if you aim to
# deploy this in a production environment.
# You can connect your own Oauth2/OpenID Connect authorization by setting the following environment parameters:
ENV CLAM_OAUTH=false
#^-- set to true to enable
ENV CLAM_OAUTH_AUTH_URL=""
#^-- example for clariah: https://authentication.clariah.nl/Saml2/OIDC/authorization
ENV CLAM_OAUTH_TOKEN_URL=""
#^-- example for clariah https://authentication.clariah.nl/OIDC/token
ENV CLAM_OAUTH_USERINFO_URL=""
#^--- example for clariah: https://authentication.clariah.nl/OIDC/userinfo
ENV CLAM_OAUTH_CLIENT_ID=""
ENV CLAM_OAUTH_CLIENT_SECRET=""
#^-- always keep this private!


ENV HF_TOKEN=""
#^-- Set to your huggingface token

# Install all global dependencies
RUN apt-get update && apt-get install -y --no-install-recommends runit curl ca-certificates nginx uwsgi uwsgi-plugin-python3 python3-pip python3-yaml python3-lxml python3-requests ffmpeg zip git

# Prepare environment
RUN mkdir -p /etc/service/nginx /etc/service/uwsgi /var/www/.cache /var/www/.config && chown www-data:www-data /var/www/.cache /var/www/.config

# Patch to set proper mimetype for CLAM's logs; maximum upload size
RUN sed -i 's/txt;/txt log;/' /etc/nginx/mime.types &&\
    sed -i 's/xml;/xml xsl;/' /etc/nginx/mime.types &&\
    sed -i 's/client_max_body_size 1m;/client_max_body_size 1000M;/' /etc/nginx/nginx.conf

# Temporarily add the sources of this webservice
COPY . /usr/src/webservice


ENV XDG_CACHE_DIR=/var/www/.cache
ENV XDG_CONFIG_DIR=/var/www/.cache
ENV TRANSFORMERS_CACHE=/var/www/.cache
ENV HF_HOME=/var/www/.cache

# Configure webserver and uwsgi server
RUN cp /usr/src/webservice/runit.d/nginx.run.sh /etc/service/nginx/run &&\
    chmod a+x /etc/service/nginx/run &&\
    cp /usr/src/webservice/runit.d/uwsgi.run.sh /etc/service/uwsgi/run &&\
    chmod a+x /etc/service/uwsgi/run &&\
    cp /usr/src/webservice/asrservice/asrservice.wsgi /etc/asrservice.wsgi &&\
    chmod a+x /etc/asrservice.wsgi &&\
    cp -f /usr/src/webservice/asrservice.nginx.conf /etc/nginx/sites-enabled/default

# Install the the service itself
RUN cd /usr/src/webservice && pip install --break-system-packages git+https://github.com/m-bain/whisperx.git && pip install --break-system-packages . && rm -Rf /usr/src/webservice /root/.cache
RUN ln -s /usr/local/lib/python3.*/dist-packages/clam /opt/clam

VOLUME ["/data"]
EXPOSE 80
WORKDIR /

ENV HOME=/var/www
ENTRYPOINT ["runsvdir","-P","/etc/service"]
