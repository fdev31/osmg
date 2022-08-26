#!/usr/bin/env -S just --justfile

venv := ".tox/" + `grep envdir tox.ini | sed 's#.*/##' `
pkg := "back"
src := "./server/back"

SERVER_PARAMS := "--ws-ping-interval 5 --ws-ping-timeout 2"
HTTP_PORT := `cat HTTP_PORT`



export PYTHONPATH := "./tests/unit/"
export NODE_ENV := "dev" # or production
export WEB_CONCURRENCY := "10"

# list available commands
default:
    @just --list

# run everything python related
py: style coverage unit types
# run everything JS related
js: production locales front
# build Javascript components in production mode
production:
    @just --set NODE_ENV production component

# make python package run from the sources
fix:
    ./scripts/install_editable {{venv}} {{pkg}}

# build translations files
locales:
    cd locales && ./build

# build Js components if changed
component:
    ./node_modules/.bin/rollup -c rollup.config.js

# run (any kind of) tests
test testfile='tests':
    {{venv}}/bin/pytest -v {{testfile}}

# run unit tests
unit: fix
    @just test ./tests/unit/

# run frontend tests
front: fix
    @just stop
    @just run 1 &
    @just test ./tests/front/

# list available events
list-events:
	@grep -rE -A5 'publishEvent' server 2>/dev/null | grep "cat=" | sed -E 's/.*cat *= *([^,)]+).*/\1/' | sed -E 's#Events.(\S+).name#\1#' | sed -E 's#^"([^"]+)"$#\1#' | uniq | sort

# run python style rules
style: fix
    {{venv}}/bin/isort {{src}} tests
    {{venv}}/bin/black {{src}} tests

# run python coverage
coverage: fix
    {{venv}}/bin/vulture {{src}} tests

# run python type checks
types: fix
    {{venv}}/bin/mypy {{src}}

# run in debug or standard mode
run debug="1": fix
    {{venv}}/bin/uvicorn back.routes:app {{SERVER_PARAMS}} --port {{HTTP_PORT}} --log-level={{ if debug == "1" {"debug --host 0.0.0.0 --log-config logging.yaml --env-file tests/front/.env"} else {"warning"} }}


# stops the http server used for testing
stop: fix
    {{venv}}/bin/procmgr stop http
