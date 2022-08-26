#!/usr/bin/env -S just --justfile

venv := ".tox/" + `grep envdir tox.ini | sed 's#.*/##' `
pkg := "back"
src := "./server/back"

SERVER_PARAMS := "--ws-ping-interval 5 --ws-ping-timeout 2"
HTTP_PORT := `cat HTTP_PORT`


export PYTHONPATH:="./tests/unit/"
export NODE_ENV := "dev" # or production

# list available commands
default:
    @just --list

py: style coverage unit types
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

# build one Js component by name or all of them if none specified
component name="":
	cd components && ./build {{ if name == "" {""} else {"src/" + name + ".vue"} }}

# run (any kind of) tests
test testfile='tests':
    {{venv}}/bin/pytest --pdb {{testfile}}

# run unit tests
unit: fix
    @just test ./tests/unit/

# run frontend tests
front: fix
    {{venv}}/bin/procmgr stop http
    {{venv}}/bin/procmgr start -n http {{venv}}/bin/uvicorn back.routes:app --host 0.0.0.0 --reload --port 5000 --log-level=debug --log-config logging.yaml --env-file ./tests/front/.env
    @just test ./tests/front/
    {{venv}}/bin/procmgr stop http

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
    export WEB_CONCURRENCY=10
    export AIOREDIS_DEBUG={{ if debug == "1" {"1"} else {"0"} }}
    export DEBUG={{ if debug == "1" {"1"} else {""} }}
    {{venv}}/bin/uvicorn back.routes:app {{SERVER_PARAMS}} --port {{HTTP_PORT}} --log-level={{ if debug == "1" {"debug --reload --host 0.0.0.0 --log-config logging.yaml"} else {"warning"} }}


