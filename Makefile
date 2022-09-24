.PHONY: clean clean-test clean-pyc clean-build docs help test test-cov
.DEFAULT_GOAL := help

clean: ## remove all build, test, coverage and Python artifacts
	@echo -----------------------------------------------------------------
	@echo CLEANING UP ...
	make clean-build clean-pyc clean-test
	@echo ALL CLEAN.
	@echo -----------------------------------------------------------------

clean-build: ## remove build artifacts
	@echo cleaning build artifacts ...
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	@echo cleaning pyc file artifacts ...
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	@echo cleaning test artifacts ...
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache


test: ## run tests (and coverage if configured in setup.cfg) with the default Python
	@echo -----------------------------------------------------------------
	@echo RUNNING TESTS...
	pytest --cov=monstermash
	@echo ✅ Tests have passed! Nice work!
	@echo -----------------------------------------------------------------


coverage: ## check code coverage quickly with the default Python
	@echo producing coverage report at COVERAGE.txt...
	coverage report > COVERAGE.txt


dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist


install: clean ## install the package to the active Python's site-packages via pip
	@echo -----------------------------------------------------------------
	@echo INSTALLING monstermash...
	pip install .
	@echo INSTALLED monstermash
	@echo - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	@echo monstermash info:
	@echo - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	pip show monstermash
	@echo -----------------------------------------------------------------


install-e: clean ## install via pip in editable mode this see https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs
	pip install -e .

test-cov: test ## run tests locally and output coverage file
	coverage report > COVERAGE.txt

commit-cov:
	git add COVERAGE.txt --force

install-all: ## install extra requirements for tests etc
	pip install -r requirements/all.txt

install-docs:
	pip install -r requirements/docs.txt

install-tests:
	pip install -r requirements/test.txt

install-dev-local: ## install all the stuff you need to develop locally
	pip install --upgrade pip
	pip install wheel
	pip install -e .
	pip install -r requirements/all.txt
	pre-commit install

publish: dist ## publish the package to PyPI
	twine upload dist/*

run-infra:
	docker-compose -f docker/dev/docker-compose.yaml up --remove-orphans -d

stop-infra:
	docker-compose -f docker/dev/docker-compose.yaml down

docs: ## generate Sphinx HTML documentation, including API docs
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
