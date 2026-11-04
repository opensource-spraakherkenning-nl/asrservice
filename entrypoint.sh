#!/bin/sh

# Entrypoint for the docker container, generates the configuration on-the-fly from the template and runtime environment variables

# shellcheck disable=SC2086
GLOBAL_ENV=1 make clean asrservice.toml && exec clam --config asrservice.toml $CLAM_EXTRA
