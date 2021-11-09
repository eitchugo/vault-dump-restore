.PHONY: clean-pyc clean-build clean build install docker docs

CURRENT_DATE := $(shell date -u +'%Y-%m-%dT%H:%M:%SZ')
APP_VERSION := $(shell python3 -c "from src.vault_dump_restore import __version__; print(__version__)")

clean-pyc:
	find . -name \*.pyc -exec rm -f {} +
	find . -name \*.pyo -exec rm -f {} +
	find . -name \*~ -exec rm -f {} +

clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf package/
	rm -rf __pycache__/
	rm -rf *.egg-info

clean: clean-pyc clean-build

build: clean-build
	pip3 install --target ./package/python .

install:
	pip3 install .

docs:
	pip3 install -r requirements-docs.txt
	$(MAKE) -C docs html
