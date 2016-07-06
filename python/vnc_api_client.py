from vnc_api.vnc_api import VncApi
from vnc_api.vnc_api import NoIdError
import requests
import argparse
import time
import uuid

DATA_MAP = {
    'conn':'ipsecsite_connection',
    'vpn':'vpnservice',
    'ike':'ikepolicy',
    'ipsec':'ipsecpolicy',
}

connected = False

while not connected:
    try:
        api = VncApi(
             "admin", "123456", "admin",
             "172.16.161.203", "8082", "/",
             auth_host="172.16.161.203", auth_port="35357",
             auth_protocol="http", auth_url="/v2.0/tokens",
             auth_type="keystone")
        connected = True
    except requests.exceptions.RequestException as e:
        time.sleep(3)


parser = argparse.ArgumentParser()
parser.add_argument(
        '--type', '-t',
        action='store',
        default='conn',
        help='Type of data')
parser.add_argument(
        '--action', '-a',
        action='store',
        default='delete',
        help='Action:create delete update')
parser.add_argument(
        'id', metavar='ID',
        help='ID')
parser.add_argument(
        '--tenant-id', '-tid',
        action='store',
        default='eba0fceb368346ce8250b2da1cb80a9b',
        help='Tenant id')
args = parser.parse_args()

def get_all_data_uuid(tp=args.type,tid=args.tenant_id):
    datas = DATA_MAP[tp]+'s'
    cmd = '_'.join([datas,'list'])
    method = getattr(api,cmd)
    ids = []
    data_list = method(parent_id=str(uuid.UUID(tid)))[datas.replace('_','-')]
    for d in data_list:
        ids.append(d['uuid'])
    return ids

def run(tp=args.type,action=args.action,id=args.id):
    data = DATA_MAP[tp]
    cmd = '_'.join([data,action])
    print cmd , id
    method = getattr(api,cmd)
    if id == 'all' and action == 'delete':
        ids = get_all_data_uuid()
        print ids
        for id in ids:
            method(id=id)
    else:
        method(id=id)

run()
#netid = u'c93c0a9a-7347-4d33-a831-a5622c137105'
#print api.virtual_network_read(id=netid)
