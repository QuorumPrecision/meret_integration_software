from email import message
from email.policy import default
import tkinter as tk
from turtle import width
from tkinter import messagebox
import data1
import serial
import sys
import json
from pprint import pprint
import tkinter.font

connect_serial_state = False
ser = None


def download_and_save_archive():
    global ser
    status_text.set("Stahujem data zo zariadenia...")
    try:
        archive_data = data1.read_archive(ser)
    except Exception as e:
        messagebox.showerror(
            "Chyba!", "Nepodarilo sa stiahnut archiv. Mate spravne nastaveny COM port?"
        )
        print("Nepodarilo sa stiahnut archiv!")
        disconnect_serial()
        return
    json_file_name = "archive_data.json"
    with open(json_file_name, "w") as outfile:
        json.dump(archive_data, outfile)
    status_text.set("{}".format(json_file_name))
    messagebox.showinfo(
        "Stav stiahnutia",
        "Archiv bol stiahnuty a ulozeny do suboru {}!".format(json_file_name),
    )
    delete_archive_from_device = messagebox.askquestion(
        "Vymazat data?", "Prajete si vymazat archiv zo zariadenia?"
    )
    if delete_archive_from_device == "yes":
        print("Vymazavam data zo zariadenia")
        data1.delete_device_archive(ser)
    else:
        print("Data zostavaju v zariadeni")


def connect_serial():
    global ser
    print("Connecting to selected serial port {}".format(serial_selected.get()))
    ser = data1.connect_serial(port=serial_selected.get())
    status_text.set("Pripojeny!")
    print("Connected!")
    button_archive.config(state="normal")
    button_connect.config(state="disabled")
    button_disconnect.config(state="normal")


def disconnect_serial():
    global ser
    ser.close()
    status_text.set("Odpojeny!")
    print("Disconnected!")
    button_archive.config(state="disable")
    button_disconnect.config(state="disabled")
    button_connect.config(state="normal")


SerialsList = data1.list_serial_ports()
if len(SerialsList) < 1:
    messagebox.showerror("Chyba", "Ani jeden seriovy port nenajdeny")
    sys.exit()


win = tk.Tk()
win.geometry("+100+100")
win.title("Data1 Archive Reader 2.0.2")
win.resizable(False, False)


frame_connection = tk.LabelFrame(win, text="Pripojenie")
frame_connection.grid(column=0, row=0, padx=10, pady=10, sticky="N")

frame_archive = tk.LabelFrame(win, text="Archiv")
frame_archive.grid(column=1, row=0, padx=10, pady=10, sticky="N")

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
button_disconnect.config(state="disabled")

buttonFont = tkinter.font.Font(size=20, weight="bold")

button_archive = tk.Button(
    frame_archive,
    text="Stiahnut archiv",
    command=download_and_save_archive,
    width=20,
    height=5,
    font=buttonFont,
    fg="red",
    borderwidth=10
)
button_archive.config(state="disable")
button_archive.grid(column=0, row=0, padx=10, pady=10)


status_text = tk.StringVar(win)
status_text.set("Cakam na pripojenie...")
status_label = tk.Entry(win, textvariable=status_text, state="disable")
status_label.grid(column=1, row=1, padx=10, pady=10)


button_close = tk.Button(win, text="Zavriet", command=win.destroy)
button_close.grid(column=0, row=1, padx=10, pady=10)

win.mainloop()
