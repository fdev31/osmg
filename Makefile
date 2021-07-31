.PHONY: test

HTTP_PORT=`cat HTTP_PORT`

all:
	(cd locales && ./build)
	(cd components && ./build)
test: 
	rm -fr screenshots
	./venv/bin/pip install -r test_requires.txt
	PYTHON_PATH=./tests/unit/ ./venv/bin/python tests_front/test_*.py

unit:
	./venv/bin/pip install requests pytest pytest-asyncio httpx redis
	HTTP_PORT=${HTTP_PORT} ./venv/bin/pytest tests/unit/*.py
