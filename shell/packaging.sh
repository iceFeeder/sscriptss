#!/usr/bin/env bash

dir=`dirname $0`

cmd_list="
do_pull
do_clear
do_fetch
do_pkg
do_all
"

function usage()
{
cat<<EOF 
`basename $0` Usage: 
    do_pull        #pull the latest code
    do_clear       #remove the old pkgs
    do_fetch       #fetch third_party_pkgs to proper places
    do_pkg         #do package only
    do_all         #do_pull do_clear do_fetch and do_pkg
EOF
}

function check_env()
{
    for env in $@
    do
        which $env >/dev/null 2>&1
        if [ $? -ne 0 ];then
            echo "Cant find $env..."
            exit 1
        fi
    done
}

function check_file_and_execute()
{
    env=$1
    file=$2
    if [ -f $file ];then
        echo "$env $file"
        $env $file
    else
        echo "no such file $file"
        exit 1
    fi
}

function do_clear()
{
    rm -rf $dir/build/artifacts/*.rpm
    rm -rf $dir/controller/build/package-build/RPMS/x86_64/*.rpm
    rm -rf $dir/controller/build/package-build/RPMS/noarch/*contrail*.rpm
}

function do_pull()
{
    check_env repo git
    repo forall -p -c git pull
}

function do_fetch()
{
    check_file_and_execute sh $dir/third_party_rpms/fetch_pkgs.sh
    check_file_and_execute python $dir/third_party/fetch_packages.py
    check_file_and_execute python $dir/distro/third_party/fetch_packages.py
}

function do_pkg()
{
    check_file_and_execute python $dir/tools/packaging/build/packager.py
}

function do_all()
{
    do_pull
    do_clear
    do_fetch
    do_pkg
}

check_env python

for cmd in $cmd_list
do
    if [ $1 == $cmd ];then
        $1
        exit 0
    fi
done

usage
exit 0
