#!/bin/bash
PY=python3

if [ ! -d venv ]; then
    $PY -m venv venv
fi
source venv/bin/activate
(cd back && $PY setup.py develop)
export PREFIX=$(pwd)
exec $VIRTUAL_ENV/bin/uvicorn back.routes:app --reload --port 5000
exec back-start front
