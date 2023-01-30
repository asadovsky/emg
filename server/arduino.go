package main

import (
	"bufio"
	"io"
	"strconv"
)

func GenValuesArduino(r io.Reader) <-chan float32 {
	c := make(chan float32)
	go func() {
		s := bufio.NewScanner(r)
		for s.Scan() {
			v, err := strconv.Atoi(s.Text())
			ok(err)
			c <- float32(v)
		}
		ok(s.Err())
	}()
	return c
}
