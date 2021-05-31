#!/bin/sh
if [ ! -d venv ]; then
    python -m venv venv
fi
source venv/bin/activate
(cd back && python setup.py install)
exec back-start front
