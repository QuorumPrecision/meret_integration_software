#!/usr/bin/env python3

from tkinter import messagebox
import serial
import serial.tools.list_ports
import struct
from pprint import pprint
import math
import datetime
import tkinter as tk
from tkinter import ttk


def checksum(by):
    sum = 0
    for b in by:
        sum = sum + b
    nbits = 8
    val = 256 - sum
    checksum = bytearray(((val + (1 << nbits)) % (1 << nbits),))
    return checksum


def get_pressure(ser, addr=255):
    req = bytearray((0x55, addr, 0x00, 0x08, 0x05, 0x10, 0x00, 0x8F))
    ser.write(req)
    ret = ser.read(11)
    value = struct.unpack("f", ret[6:10])[0]
    return value


def get_device_serial(ser, addr=255):
    # req = bytearray((0x55, addr, 0x00, 0x06, 0x01))
    req = bytearray((0x55, addr, 0x00, 0x06, 0x02))
    # req = bytearray((0x55, addr, 0x00, 0x06, 0x03))
    req = req + checksum(req)
    ser.write(req)
    ret = ser.read(50)
    value = ret[5:13].decode("UTF-8")
    return value


def get_time(ser, addr=255):
    req = bytearray((0x55, addr, 0x00, 0x07, 0x1E, 0x24))
    req = req + checksum(req)
    for r in req:
        print(" " + hex(r), end="")
    print()
    ser.write(req)
    ret = ser.read(15)
    try:
        for r in ret:
            print(" " + hex(r), end="")
        hour = ret[6]
        minute = ret[7]
        second = ret[8]
        day = ret[9]
        month = ret[10]
        year = struct.unpack(">H", ret[11:13])[0]
        out = "{}:{}:{} {}.{}. {}".format(hour, minute, second, day, month, year)
    except Exception as e:
        raise
    return out


def syn_time_from_os(ser, addr=255):
    now = datetime.datetime.now()
    req = bytearray(
        (
            0x55,
            addr,
            0x00,
            0x0F,
            0x1F,
            0x24,
            now.hour,
            now.minute,
            now.second,
            now.day,
            now.month,
        )
    )
    req = req + bytearray(struct.pack(">H", now.year)) + bytearray((0x0,))
    req = req + checksum(req)
    for r in req:
        print(" " + hex(r), end="")
    print()
    ser.write(req)
    ret = ser.read(7)
    for r in ret:
        print(" " + hex(r), end="")
    print()


def set_wakeup_time(ser, addr=255):
    print("Setting wakeup time for first record")
    now = datetime.datetime.now()
    req = bytearray(
        (
            0x55,
            addr,
            0x00,
            0x0F,
            0x1F,
            0x26,
            now.hour,
            now.minute,
            now.second + 5,
            now.day,
            now.month,
        )
    )
    req = req + bytearray(struct.pack(">H", now.year)) + bytearray((0x0,))
    req = req + checksum(req)
    for r in req:
        print(" " + hex(r), end="")
    print()
    ser.write(req)
    ret = ser.read(7)
    for r in ret:
        print(" " + hex(r), end="")
    print()


def set_archive_interval(ser, addr=255, hours=0, minutes=0, seconds=5):
    print("Setting archive interval (how often to take a reading and save to archive)")
    print(
        "Setting to hours: {} minutes: {} seconds: {}".format(hours, minutes, seconds)
    )
    req = bytearray((0x55, addr, 0x00, 0x0A, 0x1F, 0x25, hours, minutes, seconds))
    req = req + checksum(req)
    for r in req:
        print(" " + hex(r), end="")
    print()
    ser.write(req)
    ret = ser.read(7)
    for r in ret:
        print(" " + hex(r), end="")
    print()


def get_archive_interval(ser, addr=255):
    print("Get archive interval (cadence)")
    req = bytearray((0x55, addr, 0x00, 0x07, 0x1E, 0x25))
    req = req + checksum(req)
    for r in req:
        print(" " + hex(r), end="")
    print()
    ser.write(req)
    ret = ser.read(10)
    for r in ret:
        print(" " + hex(r), end="")
    out = {"hrs": ret[6], "mins": ret[7], "secs": ret[8]}
    pprint(out)
    return out


def delete_device_archive(ser, addr=255):
    req = bytearray((0x55, addr, 0x00, 0x0B, 0x1F, 0x22, 0x00, 0x00, 0x00, 0x00))
    req = req + checksum(req)
    ser.write(req)
    ret = ser.read(7)
    for b in ret:
        print(hex(b))


def list_serial_ports():
    SerialsList = []
    for port in serial.tools.list_ports.comports():
        # print(port.vid)
        print(port.hwid)
        # print(port.pid)
        # print(port.serial_number)
        # print(port.location)
        # print(port.manufacturer)
        # print(port.product)
        # print(port.interface)
        # print(port.description)
        # print(port.device)
        # print(port.name)
        if "VID" in port.hwid:
            SerialsList.append(port.device)
    return SerialsList


def connect_serial(port="COM4"):
    print("Connecting to serial port {}".format(port))
    ser = serial.Serial(
        port=port, baudrate=9600, parity=serial.PARITY_NONE, timeout=1, write_timeout=5
    )
    return ser


# gets number of samples stored in memory
def get_samples_count(ser, device_addr=255):
    req = bytearray((0x55, device_addr, 0x00, 0x07, 0x1E, 0x22))
    req = req + checksum(req)
    pprint(req)
    try:
        ser.write(req)
    except Exception as e:
        print("Unable to download data from this COM port!")
        raise
    print("get_samples_count: Waiting for response from device")
    ret = ser.read(11)
    print("Returned")
    samples = struct.unpack("f", ret[6:10])[0]
    print(samples)
    return samples


def read_archive(ser):
    archive = []
    try:
        samples_available = get_samples_count(ser)
    except Exception as e:
        raise
    segments = int(math.ceil(samples_available / 14.0))
    print("Available records: {} Segments (14 records per segment): {}".format(samples_available, segments))
    mem_addr = 0
    seg = 0
    popup = tk.Toplevel()
    popup.title("Stahujem archiv...")
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(
        popup, variable=progress_var, maximum=segments, length=800
    )
    progress_bar.grid(row=1, column=0)
    popup.pack_slaves()
    try:
        while seg < segments + 1:
            print("Reading segment {} / {}".format(seg, segments))
            info = read_bytes_from_memory(ser, mem_addr)
            archive.extend(info)
            mem_addr = mem_addr + 140
            seg = seg + 1
            popup.update()
            progress_var.set(seg)
    except Exception as e:
        print("Error raised: " + str(e))
        popup.destroy()
        raise
    popup.destroy()
    return archive


def read_bytes_from_memory(ser, mem_addr, device_addr=255):
    records = []
    archive = []
    mem_addr_bytes = struct.pack("<f", mem_addr)
    req = bytearray((0x55, device_addr, 0x00, 0x0B, 0x1E, 0x23)) + bytearray(
        mem_addr_bytes
    )
    req = req + checksum(req)
    ser.write(req)
    ret = ser.read(147)

    print("RX packet: ")
    for by in ret:
        print("{:02X} ".format(by), end="")
    print()
    rx_chksum = checksum(ret[:-1])[0]
    print("Checksum from packet: {:02X}".format(ret[-1]))
    print("Calculated checksum:  {:02X}".format(rx_chksum))

    if ret[-1] != rx_chksum:
        messagebox.showerror(
            "Error",
            "Problem stahovania dat z archivu - nesedi checksum! Skuste stiahnut archiv opat.",
        )
        print("Calculated checksum: {}".format(rx_chksum))
        raise Exception("Checksum is not correct!")

    i = 12  # records starting on 12th byte of response

    while i < 140:
        records.append(ret[i : i + 10])
        i = i + 10
    for record in records:
        archive.append(
            {
                "time_sec": record[0],
                "time_hour": record[1] >> 3,
                "time_min": (record[1] & 0x07) << 3 | record[2] >> 5,
                "time_day": record[2] & 0x1F,
                "time_month": record[3] >> 3,
                "time_dow": record[3] & 0x07,
                "time_year": struct.unpack(">H", record[4:6])[0],
                "value": struct.unpack("<f", record[6:10])[0],
            }
        )
    return archive
