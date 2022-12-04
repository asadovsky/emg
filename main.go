package main

import (
	"bufio"
	"fmt"
	"log"

	"github.com/tarm/serial"
)

func main() {
	stream, err := serial.OpenPort(&serial.Config{
		Name: "/dev/tty.usbserial-02894AD3",
		Baud: 115200,
	})
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
