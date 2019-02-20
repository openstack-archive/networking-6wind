# Copyright 2019 6WIND S.A.

PYTHON := python
DIST_DIR := dist

clean:
	find . -name "*.py[co]" -exec rm '{}' \;
	rm -rf *.egg-info/ dist/ build/
sdist:
	$(PYTHON) ./setup.py sdist --dist-dir=${DIST_DIR}

rpm:
	$(PYTHON) ./setup.py bdist_rpm --binary-only --post-install post_install.sh --post-uninstall post_remove.sh --dist-dir=${DIST_DIR}

build:
	$(PYTHON) ./setup.py build ${ARGS}

install:
	$(PYTHON) ./setup.py install ${ARGS}

develop:
	$(PYTHON) ./setup.py develop

missing_licenses:
	git grep -LiI "Copyright .* 6WIND S.A." | grep -v "^\."

.PHONY: clean sdist bdist_rpm build install missing_licenses dist develop
