SHELL := /bin/bash -euo pipefail

.DELETE_ON_ERROR:

.PHONY: run
run:
	go run . --arduino-port $(ARDUINO_PORT)

.PHONY: lint
lint:
	go vet ./...
