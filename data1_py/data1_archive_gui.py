import sys
import tkinter as tk
import tkinter.font
from tkinter import messagebox, ttk
from tkinter.filedialog import asksaveasfile

import data1

connect_serial_state = False
ser = None


def download_and_save_archive():
    global ser
    status_text.set("Stahujem data zo zariadenia...")
    try:
        samples_available = data1.get_samples_count(ser)
    except Exception as e:
        messagebox.showerror("Chyba!", str(e))
        raise
    try:
        archive_data = data1.read_archive(ser, samples_available)
    except Exception as e:
        print(str(e))
        messagebox.showerror("Chyba!", "Nepodarilo sa stiahnut archiv.")
        print("Nepodarilo sa stiahnut archiv!")
        disconnect_serial()
        return
    try:
        serial_number = data1.get_device_serial(ser)
        outfile = asksaveasfile(
            filetypes=[
                ("CSV subor", ".csv"),
            ],
            mode="w",
            defaultextension=".csv",
            initialfile=f"{serial_number}.csv",
        )
        if outfile is None:  # asksaveasfile return `None` if dialog closed with "cancel".
            raise Exception("File not selected")
    except Exception as e:
        messagebox.showerror(
            "Error ukladania suboru",
            f"Nebolo mozne otvorit subor pre zapisovanie! {str(e)}",
        )
        return
    try:
        samples_saved = 1
        outfile.write("Datum;Cas;Hladina\n\n")
        for r in archive_data:
            # 01.03.2022;11:20:16;0,73
            value = "{:.2f}".format(float(r["value"])).replace(".", ",")
            record_line = "{:02d}.{:02d}.{};{:02d}:{:02d}:{:02d};{}\n".format(
                r["time_day"],
                r["time_month"],
                r["time_year"],
                r["time_hour"],
                r["time_min"],
                r["time_sec"],
                value,
            )
            print(samples_saved, record_line, end="")
            outfile.write(record_line)
            samples_saved = samples_saved + 1
            if samples_saved >= samples_available:
                break
        outfile.close()
    except Exception as e:
        messagebox.showerror(
            "Error ukladania suboru",
            f"Nebolo mozne ulozit archivny subor! {str(e)}",
        )
        return
    messagebox.showinfo("Stav stiahnutia", "Archiv bol stiahnuty a ulozeny do suboru!")
    delete_archive_from_device = messagebox.askquestion("Vymazat data?", "Prajete si vymazat archiv zo zariadenia?")
    if delete_archive_from_device == "yes":
        print("Vymazavam data zo zariadenia")
        data1.delete_device_archive(ser)
    else:
        print("Data zostavaju v zariadeni")
    status_text.set("Data stiahnute")


def get_and_show_value():
    global ser
    try:
        time_str = data1.get_time(ser)
        current_value = round(data1.get_pressure(ser), 3)
    except Exception as e:
        value_text.set(f"Problem nacitania!! {str(e)}")
    value_text.set(f"{current_value} @ {time_str}")


def connect_serial():
    global ser
    print(f"Connecting to selected serial port {serial_selected.get()}")
    ser = data1.connect_serial(port=serial_selected.get())
    status_text.set("Pripojeny!")
    print("Connected!")
    button_archive.config(state="normal")
    button_connect.config(state="disabled")
    button_disconnect.config(state="normal")
    button_value.config(state="normal")


def disconnect_serial():
    global ser
    ser.close()
    status_text.set("Odpojeny!")
    print("Disconnected!")
    button_archive.config(state="disable")
    button_disconnect.config(state="disabled")
    button_connect.config(state="normal")
    button_value.config(state="disable")


SerialsList = data1.list_serial_ports()
if len(SerialsList) < 1:
    messagebox.showerror("Chyba", "Ani jeden seriovy port nebol najdeny")
    sys.exit()


win = tk.Tk()
win.geometry("+2+2")
win.title("Data1 Archive Reader 2.2.6")
win.resizable(False, False)

buttonFontLarge = tkinter.font.Font(size=20, weight="bold")
buttonFontMedium = tkinter.font.Font(size=15, weight="bold")

frame_connection = tk.LabelFrame(win, text="Pripojenie")
frame_connection.grid(column=0, row=0, padx=10, pady=10, sticky="N")

frame_archive = tk.LabelFrame(win, text="Archiv")
frame_archive.grid(column=1, row=0, padx=10, pady=10, sticky="N")

serials_dropdown_style = ttk.Style(frame_connection)
serials_dropdown_style.theme_use("classic")
serials_dropdown_style.configure("TCombobox", arrowsize=60)
serials_dropdown_style.configure("Vertical.TScrollbar", arrowsize=100, background="red", font=buttonFontMedium)
win.option_add("*Listbox*Font", buttonFontMedium)

serial_selected = tk.StringVar(frame_connection)
serial_selected.set("Vyberte pripojenie")
serials_dropdown = ttk.Combobox(frame_connection, textvariable=serial_selected, values=SerialsList)
serials_dropdown.config(font=buttonFontMedium)
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
value_label = tk.Entry(win, textvariable=value_text, state="disable", width=40, font=buttonFontMedium)
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
button_value.config(state="disable")


button_close = tk.Button(win, text="Zavriet", command=win.destroy, height=4, width=20)
button_close.grid(column=1, row=3, padx=10, pady=10)

win.mainloop()
