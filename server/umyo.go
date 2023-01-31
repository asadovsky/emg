package main

import (
	"bufio"
	"io"
)

type UmyoPacket struct {
	UnitId uint32
	Values []int
}

func parseUmyoPacket(buf []byte) *UmyoPacket {
	// https://github.com/ultimaterobotics/uMyo_python_tools/blob/main/umyo_parser.py
	// https://github.com/ultimaterobotics/uMyo_v2/blob/main/main.c
	p := &UmyoPacket{}
	i := 0
	p.UnitId = uint32(buf[i])
	i++
	p.UnitId <<= 8
	p.UnitId += uint32(buf[i])
	i++
	p.UnitId <<= 8
	p.UnitId += uint32(buf[i])
	i++
	p.UnitId <<= 8
	p.UnitId += uint32(buf[i])
	i++
	numValues := int(buf[i]) - 80
	i++
	assert(numValues > 0 && numValues < 40, numValues)
	i += 5
	for j := 0; j < numValues; j++ {
		hb := buf[i]
		i++
		lb := buf[i]
		i++
		v := int(hb)*(1<<8) + int(lb)
		if hb >= 1<<7 {
			v -= 1 << 16
		}
		p.Values = append(p.Values, v)
	}
	return p
}

func GenValuesUmyo(r io.Reader) <-chan float32 {
	c := make(chan float32)
	go func() {
		br := bufio.NewReader(r)
		for {
			buf := []byte{}
			for {
				b, err := br.ReadByte()
				ok(err)
				buf = append(buf, b)
				if len(buf) == 2 {
					if buf[0] == 79 && buf[1] == 213 {
						break
					}
					buf = buf[1:]
				}
			}
			packetLen := 0
			for packetLen == 0 || len(buf) < packetLen+3 {
				b, err := br.ReadByte()
				ok(err)
				buf = append(buf, b)
				if len(buf) == 5 {
					packetLen = int(buf[4])
				}
			}
			p := parseUmyoPacket(buf[5:])
			for _, v := range p.Values {
				c <- float32(v)
			}
		}
	}()
	return c
}
