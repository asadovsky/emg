SHELL := /bin/bash -euo pipefail
PATH := node_modules/.bin:$(PATH)

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

.PHONY: lint
lint: node_modules
	go vet ./...
	prettier --check .
	jshint .
