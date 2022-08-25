#!/usr/bin/env just --justfile

venv := ".tox/py310-chrome"
pkg := "back"
src := "./server/back"

SERVER_PARAMS := "--ws-ping-interval 5 --ws-ping-timeout 2"
HTTP_PORT := `cat HTTP_PORT`

export NODE_ENV := "dev" # or production

default:
    @just --list

production:
    @just --set NODE_ENV production component

fix:
    ./scripts/install_editable {{venv}} {{pkg}}

locales:
    cd locales && ./build

component name="":
	cd components && ./build {{ if name == "" {""} else {"src/" + name + ".vue"} }}

test testfile='tests':
    {{venv}}/bin/pytest --pdb {{testfile}}

unit: fix
    @just test ./tests/unit/

front: fix
    @just test ./tests/front/

events:
	@grep -rE 'publishEvent.*cat' server |sed -E 's/.*cat *= *"([^"]+) *".*/\1/' | sort

style: fix
    {{venv}}/bin/isort {{src}} tests
    {{venv}}/bin/black {{src}} tests

coverage: fix
    {{venv}}/bin/vulture {{src}} tests

types: fix
    {{venv}}/bin/mypy {{src}}

run $DEBUG="1": fix
    export WEB_CONCURRENCY=10
    export AIOREDIS_DEBUG={{ if DEBUG == "1" {"1"} else {"0"} }}
    export DEBUG={{ if DEBUG == "1" {"1"} else {""} }}
    {{venv}}/bin/uvicorn back.routes:app {{SERVER_PARAMS}} --port {{HTTP_PORT}} --log-level={{ if DEBUG == "1" {"debug --reload --host 0.0.0.0 --log-config logging.yaml"} else {"warning"} }}


