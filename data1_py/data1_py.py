#!/usr/bin/env python3

import argparse
import time
import struct
from datetime import datetime
from pprint import pprint
import sys
import serial


def get_pressure(ser, req):
    ser.write(req)
    ret = ser.read(11)
    value = struct.unpack("f", ret[6:10])[0]
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--port", help="Serial port", required=True)
    parser.add_argument("--address", help="Device address", default=0)
    parser.add_argument(
        "--cadence",
        help="How many seconds apart to request measurement",
        type=int,
        choices=range(1, 60),
        default=5,
    )
    args = parser.parse_args()

    port = args.port
    serial_baud = 9600

    print(
        "Connecting using serial port {}, parity: EVEN, baud: {}, cadence of measurement: {}s".format(
            port, serial_baud, args.cadence
        )
    )
    uart_timeout = 1
    ser = serial.Serial(
        port=port, baudrate=serial_baud, parity=serial.PARITY_EVEN, timeout=uart_timeout
    )

    addr = 255

    # fmt: off
    r = {}
    r['nazov_zariadenia'] =             bytearray((0x55, addr, 0x00, 0x06, 0x01, 0xa5))
    r['seriove_cislo'] =                bytearray((0x55, addr, 0x00, 0x06, 0x02, 0xa4))
    r['meno_programu'] =                bytearray((0x55, addr, 0x00, 0x06, 0x03, 0xa3))
    r['datum_poslednej_konfiguracie'] = bytearray((0x55, addr, 0x00, 0x06, 0x0b, 0x9b))
    r['neviemco_pravidelne'] =          bytearray((0x55, addr, 0x00, 0x07, 0x1e, 0x25, 0x62))
    r['tlak'] =                         bytearray((0x55, addr, 0x00, 0x08, 0x05, 0x10, 0x00, 0x8f))
    r['vycitanie_archivu_1'] =          bytearray((0x55, addr, 0x00, 0x0b, 0x1e, 0x23, 0x00, 0xa0, 0x03, 0x45, 0x78)) # vzdy sa vratilo 147 bytov v packete 
    r['vycitanie_archivu_2'] =          bytearray((0x55, addr, 0x00, 0x0b, 0x1e, 0x23, 0x00, 0x60, 0x0c, 0x45, 0xaf)) # 3 a 2 byte od konca ako little endian sa zvysuju vzdy o 2240
    r['vycitanie_archivu_3'] =          bytearray((0x55, addr, 0x00, 0x0b, 0x1e, 0x23, 0x00, 0x20, 0x15, 0x45, 0xe6)) # kazda odpoved ma 14 zaznamov - su ocislovane a kazdy zaznam ma por cislo (1B) a zaznam 9by
    r['vycitanie_archivu_4'] =          bytearray((0x55, addr, 0x00, 0x0b, 0x1e, 0x23, 0x00, 0xe0, 0x1d, 0x45, 0x1e)) # vsetky odpovede maju jeden posledny byte CRC
    # cislovanie v archivoch - 1_ zacina 0x32, 2 zacina 0x04, 3 zacina 0x12, 4 zacina 0x20 t.j. po precitani 64 zaznamov zacina cislovanie od zaciatku
    # fmt: on

    print(get_pressure(ser, r["tlak"]))

    while True:
        for k in r:
            ser.write(r[k])
            ret = ser.read(100)
            print(k)
            print(ret)
            time.sleep(args.cadence - uart_timeout)