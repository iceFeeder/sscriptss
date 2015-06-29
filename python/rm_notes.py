#!/usr/bin/env python

import subprocess
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("file",help="file that you want to remove the notes")
#group = parser.add_mutually_exclusive_group()

args = parser.parse_args()

if args.file and os.path.exists(args.file) :
    file = open(args.file)
    output = open(args.file.split('/')[-1]+"_output",'w')
    lines = file.readlines()
    for line in lines:
        if line[0]!='#' and line[0] != '\n':
            output.write(line)
#    subprocess.Popen("echo "+args.file,shell=True)
