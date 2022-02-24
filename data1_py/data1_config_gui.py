from email.policy import default
import tkinter as tk
from turtle import width
from tkinter import messagebox
import data1
import serial
import sys

connect_serial_state = False
ser = None


def connect_serial():
    global ser
    print("Connecting to selected serial port {}".format(serial_selected.get()))
    ser = data1.connect_serial(port=serial_selected.get())
    global connect_serial_state
    connect_serial_state = True
    current_pressure_text.set("pripojeny")


def disconnect_serial():
    global ser
    ser.close()
    global connect_serial_state
    connect_serial_state = False
    current_pressure_text.set("odpojene")
    frame_data.config(state="disable")


def get_current_samples():
    global ser
    samples = data1.get_samples_count(ser)
    current_samples.set(str(int(samples)))


def sync_time():
    global ser
    data1.syn_time_from_os(ser)
    data1.set_wakeup_time(ser)


def get_time():
    global ser
    time_str = data1.get_time(ser)
    current_time_text.set(time_str)


def set_cadence():
    global ser
    sync_time()  # this resets archive interval - must be first!
    seconds = int(cadence_label.get())
    data1.set_archive_interval(ser, seconds=seconds)
    get_cadence()


def get_cadence():
    global ser
    cadence = str(data1.get_archive_interval(ser))
    device_cadence_text.set(cadence)


def delete_archive():
    data1.delete_device_archive(ser)


def update_current_pressure_value():
    global ser
    global connect_serial_state
    print("Serial connected: {}".format(connect_serial_state))
    if connect_serial_state:
        global current_pressure_value
        current_pressure_value = round(data1.get_pressure(ser), 5)
        current_pressure_text.set("{}".format(current_pressure_value))
    else:
        current_pressure_text.set("nepripojeny")


SerialsList = data1.list_serial_ports()
if len(SerialsList) < 1:
    messagebox.showerror("Chyba", "Seriove porty nenajdene")
    sys.exit()


win = tk.Tk()
win.geometry('+400+400')
win.title("Data1 Configurator 2.0.0")

frame_connection = tk.LabelFrame(win, text="Pripojenie")
frame_connection.grid(column=0, row=0, padx=10, pady=10, sticky="N")

frame_data = tk.LabelFrame(win, text="Konfiguracia")
frame_data.grid(column=1, row=0, padx=10, pady=10, sticky="N")

serial_selected = tk.StringVar(frame_connection)
serials_dropdown = tk.OptionMenu(frame_connection, serial_selected, *SerialsList)
serials_dropdown.config(width=30)
serials_dropdown.grid(column=0, row=0, padx=10, pady=10, sticky="W", columnspan=2)

button_connect = tk.Button(frame_connection, text="Pripojit", command=connect_serial)
button_connect.grid(column=0, row=1, padx=10, pady=10, sticky="W")

button_disconnect = tk.Button(
    frame_connection, text="Odpojit", command=disconnect_serial
)
button_disconnect.grid(column=1, row=1, padx=10, pady=10, sticky="W")

button_close = tk.Button(win, text="Zavriet", command=win.destroy)
button_close.grid(column=0, row=1, padx=10, pady=10)

current_pressure_value = 0.0
current_pressure_text = tk.StringVar(frame_data)
current_pressure_text.set("Cakam na pripojenie...")
current_pressure_label = tk.Entry(
    frame_data, textvariable=current_pressure_text, state="disable", width=30
)
current_pressure_label.grid(column=1, row=0, padx=10, pady=10)

button_value = tk.Button(
    frame_data, text="Nacitat aktualnu hodnotu", command=update_current_pressure_value
)
button_value.grid(column=0, row=0, padx=10, pady=10, sticky="W")

current_time_text = tk.StringVar(frame_data)
current_time_text.set("")
current_time_label = tk.Entry(
    frame_data, textvariable=current_time_text, state="disable", width=30
)
current_time_label.grid(column=1, row=2, padx=10, pady=10)
button_time_get = tk.Button(
    frame_data, text="Nacitat cas zo zariadenia", command=get_time
)
button_time_get.grid(column=0, row=2, padx=10, pady=10, sticky="W")


button_timesync = tk.Button(
    frame_data, text="Synchronizovat cas s PC", command=sync_time
)
button_timesync.grid(column=0, row=3, padx=10, pady=10, columnspan=2)


device_cadence_text = tk.StringVar(frame_data)
device_cadence_text.set("")
cadence_label_read = tk.Entry(
    frame_data, width=30, textvariable=device_cadence_text, state="disabled"
)
cadence_label_read.grid(column=1, row=4, padx=10, pady=10)
cadence_get = tk.Button(frame_data, text="Nacitat periodu merania", command=get_cadence)
cadence_get.grid(column=0, row=4, padx=10, pady=10, sticky="W")


cadence_label = tk.Entry(frame_data, width=30)
cadence_label.grid(column=0, row=5, padx=10, pady=10)
cadence_set = tk.Button(
    frame_data, text="Nastavit periodu merania", command=set_cadence
)
cadence_set.grid(column=1, row=5, padx=10, pady=10, sticky="W")


current_samples = tk.StringVar(frame_data)
current_samples.set("")
current_samples_label = tk.Entry(
    frame_data, textvariable=current_samples, state="disable", width=30
)
current_samples_label.grid(column=1, row=6, padx=10, pady=10)
button_current_samples = tk.Button(
    frame_data, text="Nacitat pocet zaznamov v archive", command=get_current_samples
)
button_current_samples.grid(column=0, row=6, padx=10, pady=10, sticky="W")


button_deletearchive = tk.Button(
    frame_data, text="Vymazat archiv zo zariadenia", command=delete_archive
)
button_deletearchive.grid(column=0, row=7, padx=10, pady=10, columnspan=2)

win.mainloop()
