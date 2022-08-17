.PHONY: test

all:
	(cd locales && ./build)
	(cd components && ./build)

test: 
	tox

events:
	@grep -rE 'publishEvent.*cat' server |sed -E 's/.*cat *= *"([^"]+) *".*/\1/' | sort
