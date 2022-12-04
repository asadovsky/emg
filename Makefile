SHELL := /bin/bash -euo pipefail

.DELETE_ON_ERROR:

.PHONY: fmt
fmt:
	gofmt -s -w .

.PHONY: upload
upload:
	arduino-cli compile arduino/blink -b arduino:avr:uno -p $(ARDUINO_PORT) -u

.PHONY: listen
listen:
	go run main.go
