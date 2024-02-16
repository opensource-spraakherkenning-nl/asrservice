#!/bin/sh
set -e
if [ -n "$VIRTUAL_ENV" ]; then
    pip install -e .
else
    if [ -d env ]; then
        . env/bin/activate
        pip install -e .
    else
        echo "No virtual environment detected, you have to take care of running python setup.py install or setup.py develop yourself!">&2
    fi 
fi
clamservice -d asrservice.asrservice
