#!/usr/bin/env python

"""
count the num of open_file for each process,and show the max num and the relevant process.
"""

import subprocess

FILE_PATH = "./lsof_pids"
record = {}

def generate_pids():
    subprocess.call("lsof | awk '{print $2}' > " + FILE_PATH,shell=True)

def show_max_files_pro():
    pid = -1
    max_num = 1

    f = open(FILE_PATH)
    lines = f.readlines()

    for l in lines:
        if record.has_key(l[:-1]):
            record[l[:-1]] += 1
        else:
            record[l[:-1]] = 1

    for key,val in record.items():
        if record[key] > max_num:
            pid = key
            max_num = record[key]

    print "pid :",pid
    print "num :",max_num

    print "ps aux | grep "+ pid + ":"
    ret = subprocess.Popen("ps aux | grep " + pid,shell=True)
    ret.wait()
    print ret.communicate()


generate_pids()
show_max_files_pro()
