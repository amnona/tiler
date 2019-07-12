#!/usr/bin/env python

# a standalone save or open file dialog.
# prints the selected file path
# used for pygame gui using res=subprocess.run(capture_output=True) and then looking at res.stdout.strip()

import tkinter as tk
from tkinter import filedialog
import os
import sys
import argparse


def save_to_file(fileline=""):
    if os.name == 'posix':      # RPI linux
        RAMDISKpath = '/run/shm/'
    else:
        RAMDISKpath = 'C:/tmp/'

    sfiledata = RAMDISKpath + "filechoose.txt"

    fdat = open(sfiledata, "w")
    fdat.write(fileline + "\n")
    fdat.close()


def main(argv):
    parser = argparse.ArgumentParser(description='load/save dialog for pygame gui', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--save', help='save dialog (otherwise load)', action='store_true')
    args = parser.parse_args(argv)

    root = tk.Tk()
    root.withdraw()

    if args.save:
        file_path = filedialog.asksaveasfilename()
    else:
        file_path = filedialog.askopenfilename()

    if file_path:
        print(file_path)
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
