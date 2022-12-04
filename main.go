package main

import (
	"bufio"
	"fmt"
	"log"
	"os"

	"github.com/tarm/serial"
)

func main() {
	port := os.Getenv("ARDUINO_PORT")
	if port == "" {
		log.Fatal("missing ARDUINO_PORT")
	}
	stream, err := serial.OpenPort(&serial.Config{Name: port, Baud: 115200})
	if err != nil {
		log.Fatal(err)
	}
	scanner := bufio.NewScanner(stream)
	for scanner.Scan() {
		fmt.Println(scanner.Text())
	}
	if err := scanner.Err(); err != nil {
		log.Fatal(err)
	}
}
