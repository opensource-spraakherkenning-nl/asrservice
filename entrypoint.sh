#!/bin/sh

# Entrypoint for the docker container, generates the configuration on-the-fly from the template and runtime environment variables

rm -f asrservice.toml #just in case the container was persistent
make asrservice.toml && /usr/bin/clam --config asrservice.toml
