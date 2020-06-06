TWINE_CONFIG_FILE ?= .pypirc

clean-compile:
	rm -f bin/pydockenv_exec*
clean-build:
	rm -rf dist
check:
	flake8 --config .flake8
	isort -rc -c $(git ls-tree -r HEAD --name-only | grep "\.py")
build: clean check
	python setup.py sdist bdist_wheel

compile-linux-i686: GOOS = linux
compile-linux-i686: GOARCH = 386
compile-linux-x86_64: GOOS = linux
compile-linux-x86_64: GOARCH = amd64
compile-darwin: GOOS = darwin
compile-darwin: GOARCH = amd64
compile-linux-i686 compile-linux-x86_64 compile-darwin: clean-compile
	GOOS=$(GOOS) GOARCH=$(GOARCH) go build -o bin/pydockenv_exec_$(GOOS)_$(GOARCH)

compile-all: compile-linux-i686 compile-linux-x86_64 compile-darwin

build-linux-i686: PLAT_NAME = manylinux1_i686
build-linux-i686: EXEC_SUFFIX = _linux_386
build-linux-i686: compile-linux-i686
build-linux-x86_64: PLAT_NAME = manylinux1_x86_64
build-linux-x86_64: EXEC_SUFFIX = _linux_amd64
build-linux-x86_64: compile-linux-x86_64
build-darwin: PLAT_NAME = macosx_10_4_x86_64
build-darwin: EXEC_SUFFIX = _darwin_amd64
build-darwin: compile-darwin
build-linux-i686 build-linux-x86_64 build-darwin: clean-build
	mv bin/pydockenv_exec{$(EXEC_SUFFIX),}
	python setup.py bdist_wheel --plat-name $(PLAT_NAME)
	rm bin/pydockenv_exec

build-all: build-linux-i686 build-linux-x86_64 build-darwin

publish-check:
	@if [[ $$(git rev-parse --abbrev-ref HEAD) != "master" ]]; then \
		echo "error: not in master"; \
		exit 1; \
	fi; \

	@if [[ $$(git fetch | git rev-list HEAD...origin/master --count) -ne 0 ]]; then \
		echo "error: master not updated"; \
		exit 1; \
	fi; \

	git describe --exact-match HEAD

publish-pypi:
	twine check dist/*
	twine upload --config-file $(TWINE_CONFIG_FILE) --repository $(PYPI_REPOSITORY) dist/*

publish-test: PYPI_REPOSITORY = testpypi
publish-test: build-all publish-pypi
publish: PYPI_REPOSITORY = pypi
publish: build-all publish-check publish-pypi
	git push origin --tags

bump-major: PART = major
bump-minor: PART = minor
bump-patch: PART = patch

bump-major bump-minor bump-patch:
	bumpversion $(PART)

.PHONY: clean-compile clean-build check build \
	compile-linux-i686 compile-linux-x86_64 compile-darwin compile-all \
	build-linux-i686 build-linux-x86_64 build-darwin build-all \
	publish-check publish bump-major bump-minor bump-patch
