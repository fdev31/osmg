#!/usr/bin/env just --justfile

venv := ".tox/py310-chrome"
pkg := "back"
src := "./server/back"

default:
    @just --list

js:
	(cd locales && ./build)
	(cd components && ./build)

test:
    tox

fix:
    ./scripts/install_editable {{venv}} {{pkg}}

events:
	@grep -rE 'publishEvent.*cat' server |sed -E 's/.*cat *= *"([^"]+) *".*/\1/' | sort


style: fix
    {{venv}}/bin/isort {{src}}
    {{venv}}/bin/black {{src}}

coverage: fix
    {{venv}}/bin/vulture {{src}}

types: fix
    {{venv}}/bin/mypy {{src}}
