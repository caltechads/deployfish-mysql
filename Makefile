RAWVERSION = $(filter-out __version__ = , $(shell grep __version__ deployfish_mysql/__init__.py))
VERSION = $(strip $(shell echo $(RAWVERSION)))

PACKAGE = deployfish-mysql

clean:
	rm -rf *.tar.gz dist *.egg-info *.rpm
	find . -name "*.pyc" -exec rm '{}' ';'

version:
	@echo $(VERSION)
