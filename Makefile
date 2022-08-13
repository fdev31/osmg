.PHONY: test

HTTP_PORT=`cat HTTP_PORT`

all:
	(cd locales && ./build)
	(cd components && ./build)
test: 
	(cd server && tox)

mypy:
	(cd server && tox -e mypy)

unit:
	HTTP_PORT=${HTTP_PORT} ./scripts/cuspy -m pytest ../tests/unit/*.py

events:
	@grep -rE 'publishEvent.*cat' server |sed -E 's/.*cat *= *"([^"]+) *".*/\1/' | sort
