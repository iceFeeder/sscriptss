#!/usr/bin/env bash

function show_files()
{
    dir=$1
    for file in $dir/* ; do
        if [ -d $file ]; then
            show_files $file
        elif [ -w $file ]; then
            echo $file
        fi
    done
}

function reset_logs()
{
    dir=$1
    for file in $dir/* ; do
        if [ -f $file -a -w $file ]; then
            if [[ `basename $file` =~ ^.*\.log$ ]]; then
                echo  $file
                > $file
            fi
        elif [ -d $file ]; then
            reset_logs $file
        fi
    done
}

function show_logs()
{
    for file in $dir/* ; do
        if [[ `basename $file` =~ ^.*\.log$ ]]; then
            echo  `basename $file`
        fi
    done
}

reset_logs $1
