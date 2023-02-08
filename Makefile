SHELL := /bin/bash -euo pipefail
PATH := node_modules/.bin:$(PATH)

# New or modified files relative to main branch, and untracked files.
TOUCHED_PY_FILES := $(shell cat <(git diff --name-only --diff-filter=d main | grep '\.py$$') <(git ls-files -o --exclude-standard '*.py') | sort)
# All non-deleted files.
ALL_PY_FILES := $(shell comm -23 <(git ls-files -c -o --exclude-standard '*.py' | sort) <(git ls-files -d | sort))

.DELETE_ON_ERROR:

.PHONY: clean
clean:
	rm -rf node_modules

.PHONY: upload
upload:
	arduino-cli compile arduino/$(ARDUINO_SKETCH) -b arduino:avr:uno -p $(ARDUINO_PORT) -u

.PHONY: run
run:
	go run ./server --arduino-port $(ARDUINO_PORT)

.PHONY: fmt
fmt: node_modules
	gofmt -s -w .
	prettier --write .
	isort --profile black .
	black .

.PHONY: lint
lint: node_modules
	go vet ./...
	prettier --check .
	jshint .
	@if [ -z "${TOUCHED_PY_FILES}" ]; then exit 1; fi
	isort --profile black --check $(TOUCHED_PY_FILES)
	black --check $(TOUCHED_PY_FILES)
	pyright $(TOUCHED_PY_FILES)
	pylint $(TOUCHED_PY_FILES) --rcfile=.pylintrc

.PHONY: lint-all
lint-all: node_modules
	go vet ./...
	prettier --check .
	jshint .
	isort --profile black --check $(ALL_PY_FILES)
	black --check $(ALL_PY_FILES)
	pyright $(ALL_PY_FILES)
	pylint $(ALL_PY_FILES) --rcfile=.pylintrc

.PHONY: test
test:
	python -m unittest discover . '*_test.py'
