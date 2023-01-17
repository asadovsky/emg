SHELL := /bin/bash -euo pipefail
PATH := node_modules/.bin:$(PATH)

# All non-deleted files.
ALL_PY_FILES := $(shell comm -23 <(git ls-files -c -o --exclude-standard '*.py' | sort) <(git ls-files -d | sort))

.DELETE_ON_ERROR:

.PHONY: clean
clean:
	rm -rf node_modules

.PHONY: upload
upload:
	arduino-cli compile arduino/$(ARDUINO_SKETCH) -b arduino:avr:uno -p $(ARDUINO_PORT) -u

.PHONY: listen
listen:
	go run main.go --arduino-port $(ARDUINO_PORT)

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
	isort --profile black --check .
	black --check .
	pyright .
	pylint $(ALL_PY_FILES) --rcfile=.pylintrc

.PHONY: test
test:
	python -m unittest discover . '*_test.py'
