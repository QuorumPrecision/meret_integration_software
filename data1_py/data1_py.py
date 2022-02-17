#!/usr/bin/env python3

import argparse
import time
import struct
from datetime import datetime
from pprint import pprint
import sys
import serial

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--port", help="Serial port", required=True)
    parser.add_argument("--address", help="Device address", default=0)
    parser.add_argument(
        "--cadence",
        help="How many seconds apart to request measurement",
        type=int,
        choices=range(1, 60),
        default=1,
    )
    args = parser.parse_args()

    port = args.port
    serial_baud = 9600

    print(
        "Connecting using serial port {}, parity: EVEN, baud: {}, cadence of measurement: {}s".format(
            port, serial_baud, args.cadence
        )
    )
    uart_timeout = 0.9
    ser = serial.Serial(
        port=port, baudrate=serial_baud, parity=serial.PARITY_EVEN, timeout=uart_timeout
    )

    while True:
        packet = bytearray((0x00, 0x00, 0x03, 0x03, 0x07, 0x01, 0x0E))
        pprint(packet)
        ser.write(packet)
        ret = ser.read(20)
        pprint(ret)
        time.sleep(args.cadence - uart_timeout)
