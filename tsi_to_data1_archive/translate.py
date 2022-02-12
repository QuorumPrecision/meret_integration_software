#!/usr/bin/env python3

# This script will translate new TSI Archive CSV data archive to old Data 1 CSV format

from pprint import pprint
from datetime import datetime

tsifile_path = "tsi_test_archive.csv"
out_path = "data1_out_archive.csv"

print("Reading file {}".format(tsifile_path))
print("Writing to file: {}".format(out_path))

fh = open(tsifile_path, "r")
lines = fh.readlines()
fh.close()

fh = open(out_path, "w")

fh.write("Dátum;Čas;Tlak;Teplota\n\n")

# revert lines as data should be from top oldest -> bottom newest
for line in reversed(lines[1:]):
    line = line.strip()
    l = line.split(";")

    dt = datetime.strptime(l[1], "%d. %m. %Y %H:%M:%S.%f")

    date = dt.strftime("%d.%m.%Y;%H:%M:%S")
    pressure = "{:.2f}".format(float(l[2])).replace(".", ",")
    temper = "{:.2f}".format(float(l[5])).replace(".", ",")

    nl = "{};{};{}\n".format(date, pressure, temper)
    fh.write(nl)

fh.close()
print("Done")
