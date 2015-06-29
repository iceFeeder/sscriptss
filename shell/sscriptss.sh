#!/usr/bin/env bash

function reset_logs(){
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

function reset_config(){
    which openstack-config > /dev/null 2>&1
    if [ $? == 0 ]; then
        openstack-config --set /etc/contrail/contrail-api.conf DEFAULTS reset_config $1
        openstack-config --set /etc/contrail/contrail-svc-monitor.conf DEFAULTS reset_config $1
        openstack-config --set /etc/contrail/contrail-schema.conf DEFAULTS reset_config $1
        openstack-config --set /etc/contrail/contrail-discovery.conf DEFAULTS reset_config $1
    else
        echo "Can't find the openstack-config ..."
    fi
}

function contrail_services(){
    /etc/init.d/supervisor-config $1
    /etc/init.d/supervisor-control $1
    /etc/init.d/supervisor-analytics $1 
}

function rm_containers(){
    which docker > /dev/null 2>&1
    if [ $? -ne 0 ];then
        echo "Can't find docker."
        exit 0
    fi
    for i in $(docker ps -a | awk '{print $1}');do
        if [ $i != 'CONTAINER' ];then
            docker rm $i
        fi
    done
}

case "$1" in 
    contrail_services)
        contrail_services $2;;
    reset_config)
        reset_config $2;;
    rm_containers)
        rm_containers;;
    reset_logs)
        reset_logs $2;;
    *)
        echo "Usage: "
        echo "`basename $0` contrail_services start|stop|restart|status"
        echo "`basename $0` reset_logs /path"
        echo "`basename $0` rm_containers"
        echo "`basename $0` reset_config True|False";;
esac

exit 0
