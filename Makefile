
all: install

deps:
	pip install -r requirements.txt --user

install:
	pip install . --user --upgrade

uninstall:
	pip uninstall gl_utils

test:
	nosetests --rednose tests

.PHONY: init install uninstall test