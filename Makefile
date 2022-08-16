.PHONY: test

HTTP_PORT=`cat HTTP_PORT`

all:
	(cd locales && ./build)
	(cd components && ./build)

test: 
	make mypy
	make unit
	tox -e py310-chrome

black:
	tox -e black

flake:
	tox -e flake8

mypy:
	tox -e mypy | grep -v 'Call to untyped function "from_url" in typed context'

unit:
	tox -e unit -- --pdb

events:
	@grep -rE 'publishEvent.*cat' server |sed -E 's/.*cat *= *"([^"]+) *".*/\1/' | sort
