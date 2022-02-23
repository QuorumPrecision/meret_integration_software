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
    # current_pressure_label.after(200, update_current_pressure_value)


SerialsList = data1.list_serial_ports()
if len(SerialsList) < 1:
    messagebox.showerror("Chyba", "Seriove porty nenajdene")
    sys.exit()


win = tk.Tk()
# win.geometry('400x300')
win.title("Data1-PY 2022")
win.resizable(False, False)


frame_connection = tk.LabelFrame(win, text="Pripojenie")
frame_connection.grid(column=0, row=0, padx=10, pady=10, sticky="N")

frame_data = tk.LabelFrame(win, text="Data")
frame_data.grid(column=1, row=0, padx=10, pady=10, sticky="N")

frame_archive = tk.LabelFrame(win, text="Archiv")
frame_archive.grid(column=2, row=0, padx=10, pady=10, sticky="N")

frame_log = tk.LabelFrame(win, text="Log")
frame_log.grid(column=3, row=0, padx=10, pady=10, sticky="N")


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


value_label = tk.Label(frame_data, text="Aktualna hodnota:")
value_label.grid(column=0, row=0, padx=10, pady=10)

current_pressure_value = 0.0
current_pressure_text = tk.StringVar(frame_data)
current_pressure_text.set("Cakam na pripojenie...")
current_pressure_label = tk.Entry(
    frame_data, textvariable=current_pressure_text, state="disable"
)
current_pressure_label.grid(column=1, row=0, padx=10, pady=10)

button_connect = tk.Button(
    frame_data, text="Nacitat aktualnu hodnotu", command=update_current_pressure_value
)
button_connect.grid(column=0, row=1, padx=10, pady=10, sticky="W", columnspan=2)


button_archive = tk.Button(frame_archive, text="Stiahnut archiv")
button_archive.grid(column=0, row=0, padx=10, pady=10)

log_text = tk.Text(frame_log, width=40, height=20)
log_text.grid(column=0, row=0, padx=10, pady=10)


update_current_pressure_value()
win.mainloop()
