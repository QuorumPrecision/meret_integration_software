#!/usr/bin/env python3

import argparse
import time
import struct
from datetime import datetime
import sys
import serial


def calc_crc(data):
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for i in range(8):
            if (crc & 1) != 0:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return data + crc.to_bytes(2, byteorder="little")


def modbus_get_bytes(ser, funct, modbus_id, start_byte, count):
    if funct == 0x44 or funct == 0x46:
        count = int(count * 2)
    req = (
        bytearray((modbus_id, funct))
        + start_byte.to_bytes(2, byteorder="big")
        + count.to_bytes(2, byteorder="big")
    )
    req = calc_crc(req)
    # print("TX: " + req.hex())
    ser.write(req)
    ret = ser.read(20)
    # print("RX: " + ret.hex())
    return ret[3:][:-2]


def modbus_get_uint8(ser, funct, modbus_id, start_byte):
    count = 0.5
    ret = modbus_get_bytes(ser, funct, modbus_id, start_byte, count)
    ret = struct.unpack("B", ret)[0]
    return ret


def modbus_get_float(ser, funct, modbus_id, start_byte):
    count = 2
    ret = modbus_get_bytes(ser, funct, modbus_id, start_byte, count)
    ret = struct.unpack("f", ret)[0]
    return ret


def modbus_get_uint32(ser, funct, modbus_id, start_byte):
    count = 2
    ret = modbus_get_bytes(ser, funct, modbus_id, start_byte, count)
    ret = struct.unpack("I", ret)[0]
    return ret


def modbus_get_uint16(ser, funct, modbus_id, start_byte):
    count = 1
    ret = modbus_get_bytes(ser, funct, modbus_id, start_byte, count)
    ret = struct.unpack("H", ret)[0]
    return ret


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--port", help="Serial port", required=True)
    parser.add_argument("--modbus_id", help="MODBUS ID", default=1)
    parser.add_argument(
        "--cadence",
        help="How many seconds apart to request measurement",
        type=int,
        choices=range(1, 60),
        default=1,
    )
    args = parser.parse_args()

    port = args.port
    modbus_id = args.modbus_id
    serial_baud = 115200

    print("Software support: info@moirelabs.com  Version: 1.2  Author: MH")
    print(
        "Connecting using serial port {}, parity: EVEN, baud: {}, cadence of measurement: {}s".format(
            port, serial_baud, args.cadence
        )
    )
    uart_timeout = 0.9
    ser = serial.Serial(
        port=port, baudrate=serial_baud, parity=serial.PARITY_EVEN, timeout=uart_timeout
    )

    file_name = "{}.csv".format(int(time.time()))
    print("Saving to file: {}".format(file_name))
    f = open(file_name, "w", encoding="utf-8")

    primary_unit = modbus_get_uint8(ser, 0x44, modbus_id, 14562)
    primary_multiple = modbus_get_uint8(ser, 0x44, modbus_id, 14561)

    if primary_unit == 5 and primary_multiple == 11:
        unit = "kPa"
    else:
        unit = "unknown unit"

    while True:
        i = {}
        i["primary_value"] = round(modbus_get_float(ser, 0x03, modbus_id, 0x09), 3)
        data = "{},{},{},{}\n".format(
            datetime.now().isoformat(), time.time(), i["primary_value"], unit
        )
        f.write(data)
        f.flush()
        print(data, end="")
        time.sleep(args.cadence - uart_timeout)