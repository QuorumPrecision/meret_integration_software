#!/usr/bin/env python3

# tento script je na testovanie meret senzorov pripojenych napriamo k pc napr cez usb prevodnik na rs485 senzora
# takto je potrebne vygenerovat exe: pyinstaller.exe --onefile .\meret_rs485_sensor_uart_test.py

import tkinter as tk
import argparse
import serial
import serial.tools.list_ports
import struct
import sys
from pprint import pprint
from tkinter import messagebox


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
    while ser.in_waiting:
        ser.read(1)
    if args.verbose:
        print("TX: " + req.hex())
    ser.write(req)
    ret = ser.read(20)
    if args.verbose:
        print("RX: " + ret.hex())
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


def run_tests():
    baudrate = 9600
    print("Connecting using port {}".format(serial_selected.get()))
    print("Baud: {}".format(baudrate))
    print("Using MODBUS ID {}".format(modbus_id))
    i = {}
    try:
        ser = serial.Serial(port=serial_selected.get(), baudrate=baudrate, timeout=0.3)
        print("Getting primary_unit ...")
        i["primary_unit"] = modbus_get_uint8(ser, 0x44, modbus_id, 14562)
        print("Getting primary_multiple ...")
        i["primary_multiple"] = modbus_get_uint8(ser, 0x44, modbus_id, 14561)
        print("Getting primary_reading_range_min ...")
        i["primary_reading_range_min"] = modbus_get_float(ser, 0x44, modbus_id, 0x79)
        print("Getting primary_reading_range_max ...")
        i["primary_reading_range_max"] = modbus_get_float(ser, 0x44, modbus_id, 0x7D)
        print("Getting primary_reading ...")
        i["primary_reading"] = modbus_get_float(ser, 0x03, modbus_id, 0x09)
        print(i["primary_reading"])
        pprint(i)
    except Exception as e:
        err_message = "Sensor MODBUS ID {} not responding!\n{}".format(modbus_id, e)
        print(err_message)
        messagebox.showerror("Chyba!", err_message)
        ser.close()
        raise Exception(err_message)
    messagebox.showinfo("OK!", "Detekcia senzoru OK!")


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
        # if "VID" in port.hwid:
        SerialsList.append(port.device)
    return SerialsList


SerialsList = list_serial_ports()
if len(SerialsList) < 1:
    messagebox.showerror("Chyba", "Seriove porty nenajdene")
    sys.exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test Meret sensor connected using UART"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
    )
    args = parser.parse_args()

    modbus_id = 0

    win = tk.Tk()
    win.geometry("+20+20")
    win.title("Sensor Tester 1.1.0")

    serial_selected = tk.StringVar(win)
    serials_dropdown = tk.OptionMenu(win, serial_selected, *SerialsList)
    serials_dropdown.config(width=30)
    serials_dropdown.grid(column=0, row=0, padx=10, pady=10, sticky="W", columnspan=2)

    button_start_test = tk.Button(
        win, text="Spusti test", command=run_tests, width=15, height=7
    )
    button_start_test.grid(column=0, row=1, padx=10, pady=10, sticky="W")

win.mainloop()
