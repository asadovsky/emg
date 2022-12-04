SHELL := /bin/bash -euo pipefail

.DELETE_ON_ERROR:

.PHONY: fmt
fmt:
	gofmt -s -w .

.PHONY: upload
upload:
	arduino-cli compile /Users/sadovsky/dev/emg/blink -b arduino:avr:uno -p /dev/tty.usbserial-02894AD3 -u

.PHONY: listen
listen:
	go run main.go
