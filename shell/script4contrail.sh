#!/usr/bin/env bash

function reset_config(){
    which openstack-config > /dev/null 2>&1
    if [ $? == 0 ]; then
        openstack-config --set /etc/contrail/contrail-api.conf DEFAULTS reset_config $1
        openstack-config --set /etc/contrail/contrail-svc-monitor.conf DEFAULTS reset_config $1
        openstack-config --set /etc/contrail/contrail-schema.conf DEFAULTS reset_config $1
    else
        echo "Can't find the openstack-config ..."
    fi
}

function services(){
    /etc/init.d/supervisor-config $1
    /etc/init.d/supervisor-control $1
    /etc/init.d/supervisor-analytics $1 
}

case "$1" in 
    services)
        services $2;;
    reset_config)
        reset_config $2;;
    *)
        echo "Usage: "
        echo "`basename $0` services start|stop|restart|status"
        echo "`basename $0` reset_config True|False";;
esac

exit 0
