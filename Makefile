SHELL := /bin/bash -euo pipefail
PATH := node_modules/.bin:$(PATH)

.DELETE_ON_ERROR:

.PHONY: upload
upload:
	arduino-cli compile arduino/$(ARDUINO_SKETCH) -b arduino:avr:uno -p $(ARDUINO_PORT) -u

.PHONY: listen
listen:
	go run main.go --arduino-port $(ARDUINO_PORT)

.PHONY: fmt
fmt:
	gofmt -s -w .
	prettier --write .

.PHONY: lint
lint:
	go vet ./...
	prettier --check .
	jshint .
