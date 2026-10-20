#!/bin/sh

# wrapper for the background service: asrserver

if [ -d env ]; then
    . env/bin/activate
fi
exec asrserver "$@"
