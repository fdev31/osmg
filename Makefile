.PHONY: test

HTTP_PORT=`cat HTTP_PORT`

all:
	(cd locales && ./build)
	(cd components && ./build)
test: 
	rm -fr screenshots
	./venv/bin/pip install -r test_requires.txt
	PYTHONPATH=./tests/unit/ ./venv/bin/python tests_front/test_*.py

unit:
	./venv/bin/pip install requests pytest pytest-asyncio httpx redis
	HTTP_PORT=${HTTP_PORT} ./venv/bin/pytest tests/unit/*.py

events:
	@grep -rE 'publishEvent.*cat' server |sed -E 's/.*cat *= *"([^"]+) *".*/\1/' | sort
