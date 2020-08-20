SRC = $(wildcard nbs/*.ipynb)

all: eu_parliament docs

eu_parliament: $(SRC)
	nbdev_build_lib
	touch eu_parliament

docs_serve: docs
	cd docs && bundle exec jekyll serve

docs: $(SRC)
	nbdev_build_docs
	touch docs

test:
	nbdev_test_nbs

release: pypi
	nbdev_bump_version

pypi: dist
	twine upload --repository pypi dist/*

dist: clean
	python setup.py sdist bdist_wheel

clean:
	rm -rf dist