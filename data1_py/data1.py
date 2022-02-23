#!/usr/bin/env python3

import serial
import serial.tools.list_ports
import struct
from pprint import pprint


def checksum(summ):
    nbits = 8
    val = 256 - summ
    checksum = (val + (1 << nbits)) % (1 << nbits)
    return checksum


def get_pressure(ser, addr=255):
    req = bytearray((0x55, addr, 0x00, 0x08, 0x05, 0x10, 0x00, 0x8F))
    ser.write(req)
    ret = ser.read(11)
    value = struct.unpack("f", ret[6:10])[0]
    return value


def list_serial_ports():
    SerialsList = []
    for port in serial.tools.list_ports.comports():
        SerialsList.append(port.device)
        # print(port.vid)
        # print(port.interface)
        # print(port.description)
        # print(port.device)
        # print(port.name)
    return SerialsList


def connect_serial(port="COM4"):
    print("Connecting to serial port {}".format(port))
    ser = serial.Serial(port=port, baudrate=9600, parity=serial.PARITY_EVEN, timeout=1)
    return ser
