.PHONY: test

HTTP_PORT=`cat HTTP_PORT`

all:
	(cd locales && ./build)
	(cd components && ./build)
test: 
	./venv/bin/pip install -r test_requires.txt
	./venv/bin/python tests_front/test_marathon.py

unit:
	./venv/bin/pip install requests pytest pytest-asyncio httpx
	HTTP_PORT=${HTTP_PORT} ./venv/bin/pytest tests/unit/*.py
