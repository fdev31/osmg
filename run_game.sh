#!/bin/bash
PY=python3

if [ ! -d venv ]; then
    $PY -m venv venv
fi
source venv/bin/activate
(cd back && $PY setup.py install)
#exec uvicorn back.routes:app --reload
exec back-start front
