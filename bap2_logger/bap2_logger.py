#!/usr/bin/env python3

import argparse
import struct
import sys
import time
from datetime import datetime

import serial


def calc_crc(data):
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if (crc & 1) != 0:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return data + crc.to_bytes(2, byteorder="little")


def modbus_get_bytes(ser, funct, modbus_id, start_byte, count, verbose):  # pylint: disable=too-many-arguments
    if funct in (0x44, 0x46):
        count = int(count * 2)
    req = bytearray((modbus_id, funct)) + start_byte.to_bytes(2, byteorder="big") + count.to_bytes(2, byteorder="big")
    req = calc_crc(req)
    if verbose:
        print("TX: " + req.hex())
    ser.write(req)
    ret = ser.read(count * 2 + 5)
    if verbose:
        print("RX: " + ret.hex())
    return ret[3:][:-2]


def modbus_get_uint8(ser, funct, modbus_id, start_byte, verbose):
    count = 0.5
    ret = modbus_get_bytes(ser, funct, modbus_id, start_byte, count, verbose)
    ret = struct.unpack("B", ret)[0]
    return ret


def modbus_get_float(ser, funct, modbus_id, start_byte, verbose):
    count = 2
    ret = modbus_get_bytes(ser, funct, modbus_id, start_byte, count, verbose)
    ret = struct.unpack("f", ret)[0]
    return ret


def modbus_get_uint32(ser, funct, modbus_id, start_byte, verbose):
    count = 2
    ret = modbus_get_bytes(ser, funct, modbus_id, start_byte, count, verbose)
    ret = struct.unpack("I", ret)[0]
    return ret


def modbus_get_uint16(ser, funct, modbus_id, start_byte, verbose):
    count = 1
    ret = modbus_get_bytes(ser, funct, modbus_id, start_byte, count, verbose)
    ret = struct.unpack("H", ret)[0]
    return ret


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--port", help="Serial port", required=True)
    parser.add_argument(
        "--device_type", help="MERET Device type: BAP2 / BAT2 / PM121 / TM121 / PM102 / TM102", default="BAP2"
    )
    parser.add_argument("--baudrate", help="Serial baudrate", default=9600, type=int)
    parser.add_argument("--parity", help="EVEN or NONE", default="NONE")
    parser.add_argument("--modbus_id", help="MODBUS ID", default=1, type=int)
    parser.add_argument(
        "--cadence_ms",
        help="How many milliseconds apart to request measurement",
        type=float,
        default=1000,
    )
    parser.add_argument("--verbose", help="Verbose output", action="store_true")
    args = parser.parse_args()

    port = args.port
    modbus_id = args.modbus_id
    serial_baud = int(args.baudrate)
    if args.parity == "EVEN":
        parity = serial.PARITY_EVEN
    else:
        parity = serial.PARITY_NONE

    print("Software support: info@moirelabs.com  Version: 1.4  Author: MH")
    print(f"Device type: {args.device_type}")
    print(
        "Connecting using serial port {}, parity: {}, baud: {}, cadence of measurement (ms): {}".format(
            port, parity, serial_baud, args.cadence_ms
        )
    )
    uart_timeout = 1.0
    try:
        ser = serial.Serial(port=port, baudrate=serial_baud, parity=parity, timeout=uart_timeout)
    except Exception:
        print("Unable to open serial port")
        sys.exit(1)

    file_name = f"{int(time.time())}.csv"
    print(f"Saving to file: {file_name}")
    f = open(file_name, "w", encoding="utf-8")  # pylint: disable=consider-using-with

    primary_unit = 255
    primary_multiplier = 255

    if args.device_type in ("MB12", "BAP2", "BAT2"):
        try:
            primary_unit = modbus_get_uint8(ser, 0x44, modbus_id, 14562, args.verbose)
            primary_multiplier = modbus_get_uint8(ser, 0x44, modbus_id, 14561, args.verbose)
        except Exception:
            print("Unable to detect measurement unit")
        if primary_unit == 5 and primary_multiplier == 11:
            unit = "kPa"
        elif primary_unit == 1 and primary_multiplier == 0:
            unit = "C"
        else:
            unit = f"unknown unit for {args.device_type} (unit: {primary_unit}, multiplier: {primary_multiplier})"
    if args.device_type in ("MB21", "PM121", "TM121", "MB63", "MB72", "PM102", "TM102"):
        try:
            primary_unit = modbus_get_uint8(ser, 0x44, modbus_id, 14549, args.verbose)
            primary_multiplier = modbus_get_uint8(ser, 0x44, modbus_id, 14548, args.verbose)
        except Exception:
            print("Unable to detect measurement unit")
        if primary_unit == 5 and primary_multiplier == 11:
            unit = "kPa"
        elif primary_unit == 1 and primary_multiplier == 0:
            unit = "C"
        else:
            unit = f"unknown unit for {args.device_type} (unit: {primary_unit}, multiplier: {primary_multiplier})"
    if args.device_type in ("MB0101"):
        unit = ""

    print(f"Primary unit read from device: {primary_unit}")
    print(f"Primary multiplier read from device: {primary_multiplier}")

    ser.close()
    time.sleep(1)

    if args.baudrate == 115200:
        uart_timeout = 0.010
    else:
        uart_timeout = 0.095
    sleep_for = (args.cadence_ms / 1000) - uart_timeout
    print(f"Requested cadency:         {args.cadence_ms / 1000:.3f}s")
    print(f"Device to respond timeout: {uart_timeout:.3f}s")
    print(f"Sleeping between requests: {sleep_for:.3f}s")
    try:
        ser = serial.Serial(port=port, baudrate=serial_baud, parity=parity, timeout=uart_timeout)
    except Exception:
        print("Unable to open serial port")
        sys.exit(1)

    while True:
        i = {}
        try:
            i["primary_value"] = round(modbus_get_float(ser, 0x03, modbus_id, 0x09, args.verbose), 3)
        except Exception:
            print("Unable to read data from sensor!")
            time.sleep(sleep_for / 2)
            continue
        data = "{},{},{},{}\n".format(datetime.now().isoformat(), time.time(), i["primary_value"], unit)
        f.write(data)
        f.flush()
        print(data, end="")
        time.sleep(sleep_for)
