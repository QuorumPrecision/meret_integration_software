#!/usr/bin/env python3

# This script will translate new TSI Archive CSV data archive to old Data 1 CSV format

from datetime import datetime
from pprint import pprint

tsifile_path = "tsi_test_archive.csv"
out_path = "data1_out_archive.csv"

print(f"Reading file {tsifile_path}")
print(f"Writing to file: {out_path}")

with open(tsifile_path) as fh:
    lines = fh.readlines()

fh = open(out_path, "w")  # pylint: disable=consider-using-with

fh.write("Dátum;Čas;Tlak;Teplota\n\n")

# revert lines as data should be from top oldest -> bottom newest
for line in reversed(lines[1:]):
    line = line.strip()
    li = line.split(";")

    dt = datetime.strptime(li[1], "%d. %m. %Y %H:%M:%S.%f")

    date = dt.strftime("%d.%m.%Y;%H:%M:%S")
    pressure = f"{float(li[2]):.2f}".replace(".", ",")
    temper = f"{float(li[5]):.2f}".replace(".", ",")

    nl = f"{date};{pressure};{temper}\n"
    fh.write(nl)

fh.close()
print("Done")
