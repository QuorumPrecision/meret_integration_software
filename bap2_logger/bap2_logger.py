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
    ret = ser.read(count * 2 + 5)
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
    parser.add_argument("--baudrate", help="Serial baudrate", default=9600)
    parser.add_argument("--parity", help="EVEN or NONE", default="NONE")
    parser.add_argument("--modbus_id", help="MODBUS ID", default=1, type=int)
    parser.add_argument(
        "--cadence_ms",
        help="How many milliseconds apart to request measurement",
        type=float,
        default=1,
    )
    args = parser.parse_args()

    port = args.port
    modbus_id = args.modbus_id
    serial_baud = int(args.baudrate)
    if args.parity == "EVEN":
        parity = serial.PARITY_EVEN
    else:
        parity = serial.PARITY_NONE

    print("Software support: info@moirelabs.com  Version: 1.4  Author: MH")
    print(
        "Connecting using serial port {}, parity: {}, baud: {}, cadence of measurement (ms): {}".format(
            port, parity, serial_baud, args.cadence_ms
        )
    )
    uart_timeout = 0.095
    ser = serial.Serial(
        port=port, baudrate=serial_baud, parity=parity, timeout=uart_timeout
    )

    file_name = "{}.csv".format(int(time.time()))
    print("Saving to file: {}".format(file_name))
    f = open(file_name, "w", encoding="utf-8")

    primary_unit = modbus_get_uint8(ser, 0x44, modbus_id, 14562)
    primary_multiplier = modbus_get_uint8(ser, 0x44, modbus_id, 14561)

    if primary_unit == 5 and primary_multiplier == 11:
        unit = "kPa"
    elif primary_unit == 1 and primary_multiplier == 0:
        unit = "C"
    elif primary_unit == 1 and primary_multiplier == 1:
        unit = "atto C"
    else:
        unit = f"unknown unit ({primary_unit} / {primary_multiplier})"

    sleep_for = (args.cadence_ms / 1000) - uart_timeout
    print(f"Requested cadency:         {args.cadence_ms:.3f}s")
    print(f"Device to respond timeout: {uart_timeout:.3f}s")
    print(f"Sleeping between requests: {sleep_for:.3f}s")

    while True:
        i = {}
        try:
            i["primary_value"] = round(modbus_get_float(ser, 0x03, modbus_id, 0x09), 3)
        except Exception as e:
            print("Unable to read data from sensor!")
            continue
        data = "{},{},{},{}\n".format(
            datetime.now().isoformat(), time.time(), i["primary_value"], unit
        )
        f.write(data)
        f.flush()
        print(data, end="")
        time.sleep(sleep_for)
