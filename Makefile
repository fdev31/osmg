.PHONY: test

HTTP_PORT=`cat HTTP_PORT`

all:
	(cd locales && ./build)
	(cd components && ./build)
test: 
	tox

mypy:
	tox -e mypy

unit:
	./scripts/cuspy -m pytest --pdb '../tests/unit/test_*.py'

events:
	@grep -rE 'publishEvent.*cat' server |sed -E 's/.*cat *= *"([^"]+) *".*/\1/' | sort
