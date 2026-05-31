.PHONY: clean clean-test clean-pyc clean-build docs help test test-cov
.DEFAULT_GOAL := help

VERSION=1.13.1

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
	find . -name '*.egg' -o -name '*.egg' -type d -exec rm -fr {} +
	rm -fr site

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
	rm -fr .mypy_cache
	rm -fr .hypothesis


test: ## run tests (and coverage if configured in setup.cfg) with the default Python
	@echo -----------------------------------------------------------------
	@echo RUNNING TESTS...
	uv run pytest --cov=monstermash
	@echo ✅ Tests have passed! Nice work!
	@echo -----------------------------------------------------------------


coverage: ## check code coverage quickly with the default Python
	@echo producing coverage report at COVERAGE.txt...
	coverage report > COVERAGE.txt

test-ci:
	uv run pytest --cov=monstermash --cov-report=json


dist: clean ## builds source and wheel package
	uv build
	ls -l dist


install: clean ## install the package to the active Python's site-packages via pip
	@echo -----------------------------------------------------------------
	@echo INSTALLING monstermash...
	uv sync
	@echo INSTALLED monstermash
	@echo -----------------------------------------------------------------


install-e: clean ## install via pip in editable mode this see https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs
	uv pip install -e .

test-cov: test ## run tests locally and output coverage file
	coverage report > COVERAGE.txt

commit-cov:
	git add COVERAGE.txt --force

install-docs:
	uv sync --extra docs

install-tests:
	uv sync --extra test

install-all:
	uv sync --all-extras

install-dev-local: ## install all the stuff you need to develop locally
	pip install --upgrade pip
	pip install wheel
	uv sync --all-extras
	pre-commit install

publish: dist ## publish the package to PyPI
	uv publish --repository ubank

run-infra:
	docker-compose -f docker/dev/docker-compose.yaml up --remove-orphans -d

stop-infra:
	docker-compose -f docker/dev/docker-compose.yaml down

docs: ## generate Sphinx HTML documentation, including API docs
	mkdocs build html

tag:
	git tag v$(VERSION)
	git push origin v$(VERSION)

configure-poetry-for-publishing:
	poetry config http-basic.ubank aws $(aws codeartifact get-authorization-token --domain ubank --query authorizationToken --output text)