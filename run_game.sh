#!/bin/bash
PY=python3
ENVDIR=.tox/py310

HTTP_PORT=$(cat HTTP_PORT)

if [ ! -d ${ENVDIR} ]; then
    $PY -m venv ${ENVDIR}
fi
source ${ENVDIR}/bin/activate
(cd server && pip install -e .)
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
