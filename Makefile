.PHONY: test

all:
	(cd locales && ./build)
	(cd components && ./build)
test: 
	./venv/bin/pip install -r test_requires.txt
	./venv/bin/python tests_front/test_marathon.py

