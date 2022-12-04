SHELL := /bin/bash -euo pipefail

.DELETE_ON_ERROR:

.PHONY: upload
upload:
	arduino-cli compile arduino/$(ARDUINO_SKETCH) -b arduino:avr:uno -p $(ARDUINO_PORT) -u

.PHONY: listen
listen:
	go run main.go

.PHONY: fmt
fmt:
	gofmt -s -w .

.PHONY: lint
lint:
	go vet ./...
