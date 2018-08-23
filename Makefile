all:
	@echo "make devenv	- Configure the development environment"
	@echo "make test	- Run tests"
	@echo "make clean	- Remove files created by distutils and tox"
	@echo "make build	- Build sdist & bdist packages"
	@echo "make upload	- Upload to pypi"
	@exit 0

NAME:=$(shell python3 setup.py --name)
VERSION:=$(shell python3 setup.py --version | sed 's/+/-/g')

bump:
	python3 bump.py ramlpy/version.py

build: bump
	rm -fr dist
	python3 setup.py sdist bdist_wheel

upload: build
	twine upload dist/*

test:
	tox

clean:
	rm -fr *.egg-info .tox dist

devenv: clean
	rm -rf env
	virtualenv -p python3.7 env
	env/bin/pip install -Ue '.'
	env/bin/pip install -Ue '.[develop]'
