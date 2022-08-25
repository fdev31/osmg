#!/usr/bin/env just --justfile

venv := ".tox/py310-chrome"
pkg := "back"
src := "./server/back"

export NODE_ENV := "dev" # or production

default:
    @just --list

production:
    @just --set NODE_ENV production component

fix:
    ./scripts/install_editable {{venv}} {{pkg}}

locales:
    (cd locales && ./build)

component name="":
	(cd components && ./build {{ if name == "" {""} else {"src/" + name + ".vue"} }})

test testfile='tests':
    {{venv}}/bin/pytest --pdb {{testfile}}

unit: fix
    {{venv}}/bin/pytest --pdb ./tests/unit/

front: fix
    {{venv}}/bin/pytest --pdb ./tests/front/

events:
	@grep -rE 'publishEvent.*cat' server |sed -E 's/.*cat *= *"([^"]+) *".*/\1/' | sort


style: fix
    {{venv}}/bin/isort {{src}} tests
    {{venv}}/bin/black {{src}} tests

coverage: fix
    {{venv}}/bin/vulture {{src}} tests

types: fix
    {{venv}}/bin/mypy {{src}}
