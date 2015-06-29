#!/usr/bin/env python

import subprocess
import argparse

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("-l","--ls",help="test optional...",action="store_true")

args = parser.parse_args()

if args.ls:
    subprocess.Popen("ls .",shell=True)
