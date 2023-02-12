SHELL := /bin/bash -euo pipefail
PATH := node_modules/.bin:$(PATH)

.DELETE_ON_ERROR:

.PHONY: upload
upload:
	arduino-cli compile arduino/$(ARDUINO_SKETCH) -b arduino:avr:uno -p $(ARDUINO_PORT) -u

.PHONY: run
run:
	go run ./server --arduino-port $(ARDUINO_PORT)

.PHONY: test
test:
	python -m unittest discover . '*_test.py'

########################################
# Clean, format, and lint

.PHONY: clean
clean:
	rm -rf node_modules

.PHONY: fmt
fmt: node_modules
	@./fmt_or_lint.sh -f

.PHONY: lint
lint: node_modules
	@./fmt_or_lint.sh

.PHONY: lint-all
lint-all: node_modules
	@./fmt_or_lint.sh -a
