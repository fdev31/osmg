.PHONY: test

HTTP_PORT=`cat HTTP_PORT`

all:
	(cd locales && ./build)
	(cd components && ./build)

test: 
	tox

black:
	tox -e black

flake:
	tox -e flake8

mypy:
	tox -e mypy

unit:
	tox -e unit -- --pdb

events:
	@grep -rE 'publishEvent.*cat' server |sed -E 's/.*cat *= *"([^"]+) *".*/\1/' | sort
