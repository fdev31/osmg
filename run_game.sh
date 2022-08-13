#!/bin/bash
PY=python3
ENVDIR=.tox/py310-chrome

HTTP_PORT=$(cat HTTP_PORT)

source ${ENVDIR}/bin/activate
export PREFIX=$(pwd)
if [ -z "$DEBUG" ]; then
    export WEB_CONCURRENCY=10
    echo "Running standard mode"
    exec $VIRTUAL_ENV/bin/uvicorn back.routes:app --port $HTTP_PORT --log-level=warning --log-config logging.yaml
else
    echo "Running debug mode"
    export DEBUG
    exec $VIRTUAL_ENV/bin/uvicorn back.routes:app --host 0.0.0.0 --reload --port $HTTP_PORT --log-level=debug --log-config logging.yaml
fi
