#!/usr/bin/env sh

cfg_files="
/etc/nova/nova.conf
/etc/keystone/keystone.conf
/etc/glance/glance-api.conf
/etc/cinder/cinder.conf
/etc/ceilometer/ceilometer.conf
/etc/neutron/neutron.conf
"

cmd_list="
status
set_rabbit_hosts
set_rabbit_hosts_compute
reset_rabbit_hosts
reset_rabbit_hosts_compute
"

function usage()
{
cat<<EOF 
`basename $0` Usage: 
    status #show cfg status
    set_rabbit_hosts #exec in controller nodes for host list cfg
    set_rabbit_hosts_compute #exec in compute nodes for host list cfg
    reset_rabbit_hosts #exec in controller nodes for reset to vip and port 5673
    reset_rabbit_hosts_compute #exec in compute nodes for reset to vip and port 5673
EOF
}

role="controller"

# need to be filled depending on circumstances
rabbit_list="192.168.80.10:5672,192.168.80.11:5672,192.168.80.12:5672"
vip="192.168.80.100"

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

function disable_rabbit_host()
{
    echo "sed -i -e 's/^rabbit_host =/#rabbit_host =/g' $1"
    sed -i -e 's/^rabbit_host/#rabbit_host/g' $1
}

function restart_services()
{
    if [ $role == "controller" ];then
        echo "service supervisor-openstack restart"
        service supervisor-openstack restart
        service neutron-server restart
        service openstack-ceilometer-api restart
        service openstack-ceilometer-collector restart
        service openstack-ceilometer-notification restart
        chkconfig --list | grep openstack-ceilometer-central | grep on
        if [ $? -eq 0 ];then
            service openstack-ceilometer-central restart
        fi
    else
        echo "service openstack-nova-compute restart"
        service openstack-nova-compute restart
        service openstack-ceilometer-compute restart
    fi
}

function set_rabbit_hosts()
{
    status
    check_env openstack-config
    for cfg in $cfg_files
    do
        cp $cfg $cfg`date +%s`"_bak"
        disable_rabbit_host $cfg
        openstack-config --set $cfg DEFAULT rabbit_hosts $rabbit_list
        openstack-config --set $cfg DEFAULT rabbit_port 5672
    done
    restart_services
    status
}

function reset_rabbit_hosts()
{
    status
    check_env openstack-config
    for cfg in $cfg_files
    do
        cp $cfg $cfg`date +%s`"_rbak"
        disable_rabbit_host $cfg
        openstack-config --set $cfg DEFAULT rabbit_host $vip
        openstack-config --set $cfg DEFAULT rabbit_port 5673
    done
    restart_services
    status
}

function set_compute()
{
    cfg_files="
/etc/nova/nova.conf
/etc/ceilometer/ceilometer.conf
"
    role="compute"
}

function set_rabbit_hosts_compute()
{
    set_compute
    set_rabbit_hosts
}

function reset_rabbit_hosts_compute()
{
    set_compute
    reset_rabbit_hosts
}

function status()
{
    for cfg in $cfg_files
    do
        echo "---- in "$cfg" ----"
        cat $cfg | grep -E '(rabbit_host|rabbit_port)'
        echo ""
    done
}

for cmd in $cmd_list
do
    if [ $1 == $cmd ];then
        $1
        exit 0
    fi
done
usage
