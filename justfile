#!/usr/bin/env -S just --justfile

venv := ".tox/" + `grep envdir tox.ini | sed 's#.*/##' `
pkg := "back"
src := "./server/back"

SERVER_PARAMS := "--ws-ping-interval 5 --ws-ping-timeout 2"
HTTP_PORT := `cat HTTP_PORT`


export MYPYPATH := "pystubs"
export PYTHONPATH := "./tests/"
export NODE_ENV := "dev" # or production
export WEB_CONCURRENCY := "1"

# list available commands
default:
    @just --list

# Deploy the pie
deploy: prod
    ./scripts/copyCra

# removes & re-install everything
cleanenv:
    rm -fr .tox
    rm -fr node_modules
    npm i -D
    tox -e style

    just dev

# start a live dev session
live:
    ./node_modules/.bin/vite --host 0.0.0.0

# build js in dev mode
dev: gamelist locales
    ./node_modules/.bin/vite build --mode dev

# build js in dev production mode
prod: gamelist locales
    ./node_modules/.bin/vite build --mode production

# make python package run from the sources
fix:
    ./scripts/install_editable {{venv}} {{pkg}}

# builds the gamelist
gamelist:
   ./scripts/genGameList.py

# generate a bundle with all translations (updates a file in src)
locales:
    cd locales && ./build

# run (any kind of) tests
test testfile='tests/front/': dev
    {{venv}}/bin/pytest -s -v {{testfile}}

# run unit tests
unit: fix
    @just test ./tests/unit/

# list available events
list-events:
	@grep -rE -A5 'publishEvent' server 2>/dev/null | grep "cat=" | sed -Ee 's/.*cat *= *([^,)]+).*/\1/' -e 's#Events.(\S+).name#\1#' -e 's#^"([^"]+)"$#\1#' | uniq | sort

# check JS linting rules
jslint *args='src':
    npm run lint {{args}}

# check PY linting rules
pylint *args='server': fix
    {{venv}}/bin/isort  {{args}}
    {{venv}}/bin/black  {{args}}
    {{venv}}/bin/vulture  {{args}}
    {{venv}}/bin/mypy --exclude 'pystubs/*' {{args}}

# run in debug or standard mode
run debug="1": fix
    {{venv}}/bin/uvicorn back.routes:app {{SERVER_PARAMS}} --port {{HTTP_PORT}} --log-level={{ if debug == "1" {"debug --host 0.0.0.0 --log-config logging.yaml --env-file env"} else {"warning"} }}


# stops the http server used for testing
stop: fix
    {{venv}}/bin/procmgr stop http
