FROM nvidia/cuda:13.4.3-base-ubuntu26.04

LABEL org.opencontainers.image.authors="Maarten van Gompel <proycon@anaproy.nl>"
LABEL description="An Automatic Speech Recognition webservice powered by WhisperX (ASR) and CLAM (webservice), set up for NVIDIA GPUs"

# By default, there is no authentication on the service,
# which is most likely not what you want if you aim to
# deploy this in a production environment.
# You can connect your own Oauth2/OpenID Connect authorization by setting the following environment parameters
# *AND* mounting files you references here into the container
ENV CLAM_OIDC_CONFIG_FILE=""

# Same for HTTP Basic Authentication:
ENV CLAM_USER_FILE=""

ENV CLAM_URL="http://127.0.0.1:8080"
ENV CLAM_ROOT="./data"

ENV CLAM_LISTEN="0.0.0.0:8080"
ENV CLAM_TERMS_OF_SERVICE=""

#Set this to your huggingface token
ENV HF_TOKEN=""

# Install all global dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends cargo rustc curl ca-certificates netcat-openbsd make python3-pip ffmpeg zip git gettext-base && \
    cargo install --root /usr --git https://codeberg.org/proycon/clam --branch clam-4.0 && \
    pip install --break-system-packages git+https://github.com/Andrej730/whisperX@support-python-3.14 #this is temporary until whisperX > 3.8.6 is released, clam from git is also temporary until 4.0 is released on crates.io

# Add the sources of this webservice
COPY . /usr/src/webservice

ENV XDG_CACHE_DIR=/var/cache
ENV XDG_CONFIG_DIR=/var/cache
ENV TRANSFORMERS_CACHE=/var/cache
ENV HF_HOME=/var/cache
ENV HOME=/usr/src/webservice
WORKDIR /usr/src/webservice

# Install the service itself and cleanup unneeded sources afterwards
RUN cd /usr/src/webservice && GLOBAL_ENV=1 make clean all && rm -Rf /usr/src/webservice/asrserver /root/.cache /root/.cargo && apt-get remove -y cargo

VOLUME ["/data"]
EXPOSE 8080

RUN python3 -c "import nltk; nltk.download('punkt_tab')"
USER 1000
ENTRYPOINT ["/usr/bin/clam","--config","asrservice.toml"]
