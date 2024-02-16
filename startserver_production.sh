#!/bin/sh
set -e
docker build -t "asrservice" .

#Note, this datadir will be non-persistent, you will likely want to change this in production settings
[ -z "$DATADIR" ] && DATADIR=$(mktemp -d)
chmod go+wx "$DATADIR" #allow subuids/subgids to make directories, needed to prevent permission denied errors
HOST_PORT=8080

#At this point you can pass any environment variables you use in your asrservice.config.yml, pass them via --env
docker run --rm --volume "$DATADIR:/data" -p "$HOST_PORT:80" --env CLAM_ROOT=/data/asrservice-userdata --env CLAM_USE_FORWARDED_HOST=0 "asrservice"

# Note: if your host system uses SELinux and you find the data is not properly writable from the container then you might need to change --volume parameter to "$DATADIR:/data:z"

# In many production scenarios, you will not invoke this script manually but instead use a kubernetes deployment (setting the necessary env variables) or a docker-compose.yml
# It is strongly recommended to deploy the container behind a reverse proxy that handles SSL, make sure to pass CLAM_USER_FORWARDED_HOST=1 when running the container in that case.

echo "Navigate to http://localhost:8080 to access the deployed webservice"
