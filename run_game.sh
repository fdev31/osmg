#!/bin/bash
PY=python3

if [ ! -d venv ]; then
    $PY -m venv venv
fi
source venv/bin/activate
(cd back && $PY setup.py develop)
export PREFIX=$(pwd)
if [ -z "$DEBUG" ]; then
    export WEB_CONCURRENCY=1
    exec $VIRTUAL_ENV/bin/uvicorn back.routes:app --port 5000
else
    exec $VIRTUAL_ENV/bin/uvicorn back.routes:app --reload --port 5000
fi
#exec back-start front
