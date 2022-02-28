import tkinter as tk
from tkinter import messagebox
import data1
import serial
import sys
import json
from pprint import pprint
import tkinter.font
import configparser
from os import path

connect_serial_state = False
ser = None
config = configparser.ConfigParser()
config.read("data1_config.ini")


def download_and_save_archive():
    global ser
    status_text.set("Stahujem data zo zariadenia...")
    try:
        archive_data = data1.read_archive(ser)
    except Exception as e:
        print(str(e))
        messagebox.showerror(
            "Chyba!", "Nepodarilo sa stiahnut archiv. Mate spravne nastaveny COM port?"
        )
        print("Nepodarilo sa stiahnut archiv!")
        disconnect_serial()
        return
    json_file_name = "{}/archive_data.json".format(
        config["archive"]["archive_save_path"]
    )
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


def get_and_show_value():
    global ser
    try:
        time_str = data1.get_time(ser)
        current_value = round(data1.get_pressure(ser), 3)
    except Exception as e:
        value_text.set("Problem nacitania!!".format(str(e)))
    value_text.set("{} @ {}".format(current_value, time_str))


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


archive_path = "{}".format(config["archive"]["archive_save_path"])
if not path.exists(archive_path):
    print(
        "Cesta na ulozenie archivu nie je nastavena, alebo adresar neexistuje: {}".format(
            archive_path
        )
    )
    sys.exit()
print("Adresar kam sa bude ukladat archiv: {}".format(archive_path))

SerialsList = data1.list_serial_ports()
if len(SerialsList) < 1:
    messagebox.showerror("Chyba", "Ani jeden seriovy port nenajdeny")
    sys.exit()


win = tk.Tk()
win.geometry("+100+100")
win.title("Data1 Archive Reader 2.0.2")
win.resizable(False, False)

buttonFontLarge = tkinter.font.Font(size=20, weight="bold")
buttonFontMedium = tkinter.font.Font(size=15, weight="bold")

frame_connection = tk.LabelFrame(win, text="Pripojenie")
frame_connection.grid(column=0, row=0, padx=10, pady=10, sticky="N")

frame_archive = tk.LabelFrame(win, text="Archiv")
frame_archive.grid(column=1, row=0, padx=10, pady=10, sticky="N")

serial_selected = tk.StringVar(frame_connection)
serials_dropdown = tk.OptionMenu(frame_connection, serial_selected, *SerialsList)
serials_dropdown.config(font=buttonFontMedium)
serials_dropdown.config(width=30)
menu = win.nametowidget(serials_dropdown.menuname)
menu.config(font=buttonFontMedium)
serials_dropdown.grid(column=0, row=0, padx=10, pady=10, sticky="W", columnspan=2)

button_connect = tk.Button(
    frame_connection,
    text="Pripojit",
    command=connect_serial,
    width=15,
    height=3,
    font=buttonFontMedium,
)
button_connect.grid(column=0, row=1, padx=10, pady=10, sticky="W")

button_disconnect = tk.Button(
    frame_connection,
    text="Odpojit",
    command=disconnect_serial,
    width=15,
    height=3,
    font=buttonFontMedium,
)
button_disconnect.grid(column=1, row=1, padx=10, pady=10, sticky="W")
button_disconnect.config(state="disabled")

buttonFontLarge = tkinter.font.Font(size=20, weight="bold")

button_archive = tk.Button(
    frame_archive,
    text="Stiahnut archiv",
    command=download_and_save_archive,
    width=20,
    height=5,
    font=buttonFontLarge,
    fg="red",
    borderwidth=10,
)
button_archive.config(state="disable")
button_archive.grid(column=0, row=0, padx=10, pady=10)


status_text = tk.StringVar(win)
status_text.set("Cakam na pripojenie...")
status_label = tk.Entry(
    win,
    textvariable=status_text,
    state="disable",
    width=40,
    font=buttonFontMedium,
)
status_label.grid(column=1, row=1, padx=10, pady=10)


value_text = tk.StringVar(win)
value_text.set("")
value_label = tk.Entry(
    win, textvariable=value_text, state="disable", width=40, font=buttonFontMedium
)
value_label.grid(column=1, row=2, padx=10, pady=10)
button_value = tk.Button(
    win,
    text="Nacitat hodnotu\n a cas",
    command=get_and_show_value,
    width=15,
    height=3,
    font=buttonFontMedium,
)
button_value.grid(column=0, row=2, padx=10, pady=10)


button_close = tk.Button(win, text="Zavriet", command=win.destroy, height=4, width=20)
button_close.grid(column=1, row=3, padx=10, pady=10)

win.mainloop()
