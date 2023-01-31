"""Prints uMyo values."""

import dataclasses

import serial
from serial.tools import list_ports


@dataclasses.dataclass
class UmyoPacket:
    unit_id: int = 0
    values: list[int] = dataclasses.field(default_factory=list)


def parse_umyo_packet(buf: bytes) -> UmyoPacket:
    # https://github.com/ultimaterobotics/uMyo_python_tools/blob/main/umyo_parser.py
    # https://github.com/ultimaterobotics/uMyo_v2/blob/main/main.c
    p = UmyoPacket()
    i = 0
    p.unit_id = buf[i]
    i += 1
    p.unit_id <<= 8
    p.unit_id += buf[i]
    i += 1
    p.unit_id <<= 8
    p.unit_id += buf[i]
    i += 1
    p.unit_id <<= 8
    p.unit_id += buf[i]
    i += 1
    num_values = buf[i] - 80
    i += 1
    assert 0 < num_values < 40, num_values
    i += 5
    for _ in range(num_values):
        hb = buf[i]
        i += 1
        lb = buf[i]
        i += 1
        v = hb * (1 << 8) + lb
        if hb >= 1 << 7:
            v -= 1 << 16
        p.values.append(v)
    return p


def main() -> None:
    port = list_ports.comports()[-1].device
    s = serial.Serial(port=port, baudrate=921600)
    while True:
        buf = bytearray()
        while True:
            b = s.read()[0]
            buf.append(b)
            if len(buf) == 2:
                if buf[0] == 79 and buf[1] == 213:
                    break
                buf = buf[1:]
        packet_len = 0
        while packet_len == 0 or len(buf) < packet_len + 3:
            b = s.read()[0]
            buf.append(b)
            if len(buf) == 5:
                packet_len = buf[4]
        p = parse_umyo_packet(buf[5:])
        for v in p.values:
            print(v)


if __name__ == "__main__":
    main()
