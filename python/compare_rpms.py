#!/usr/bin/env python

import sys
import os


def provision():
    os.system("mkdir -p ./cmp_results")
    os.system("rm -rf ./cmp_results/*")

def get_set(path,tag="-2.0"):
    list = []
    os.system("ls -l "+path+"|awk '{print $9}'| awk -F '"+tag+"' '{print $1}' > ./cmp_results/temp")
    file = open("./cmp_results/temp")
    lines = file.readlines()
    for line in lines:
        if line !='\n' and line[-4:-1]!="rpm":
            list.append(line[0:-1])
    return set(list)
 
if len(sys.argv) == 3:
    provision()
    dir1 = sys.argv[1]
    dir2 = sys.argv[2]
    set1 = get_set(dir1,'el6')
    set2 = get_set(dir2,'el6')
    s = list(set1&set2)
    for name in s:
        os.system("rpm -qlp "+dir1+"/"+name+"* > ./cmp_results/cache1")
        os.system("rpm -qlp "+dir2+"/"+name+"* > ./cmp_results/cache2")
        os.system("diff -d ./cmp_results/cache1 ./cmp_results/cache2 > ./cmp_results/temp")
        output = open("./cmp_results/"+name+".diff",'w')
        input = open("./cmp_results/temp")
        for line in input.readlines():
            if line[0] != '<' and line[0] != '>' or line[-4:-1]=="pyo" or line[-4:-1]=="pyc":
                continue
            output.write(line)

    
else:
    print "input error..."

