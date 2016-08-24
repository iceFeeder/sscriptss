import libvirt
import sys
import time
import base64
from libvirt_qemu import qemuAgentCommand
from oslo_serialization import jsonutils
from novaclient import utils

def connect_auth_cb(creds, opaque):
    if len(creds) == 0:
        return 0

auth = [[2, 6, 8, 5, 7, 9], connect_auth_cb, None]
uri = 'qemu:///system'

conn = libvirt.openAuth(uri,auth)
dom = conn.lookupByName("instance-00000682")

command = sys.argv[1]

cmd_name = command.split()[0]

cmd = '{"execute": "guest-exec",' \
      ' "arguments":{"path": "/Windows/System32/%s", "arg": ["%s"],\
      "capture-output":true,"has_capture_output":true}}'\
      % (cmd_name, '","'.join(command.split()[1:]))

try:
    ret = qemuAgentCommand(dom, cmd, 20, 0)
    out = jsonutils.loads(ret)
    pid = out['return']['pid']
    cmd_status = '{"execute": "guest-exec-status",' \
                 ' "arguments":{"pid": %s}}' % pid
    time.sleep(3)
    ret = qemuAgentCommand(dom, cmd_status, 20, 0)
    out = jsonutils.loads(ret)
    ret = {"command" : command}
    ret.update(out['return'])
    if 'out-data' in ret:
        ret['out-data'] = base64.b64decode(ret['out-data']) #.decode("GB2312")
    if 'err-data' in ret:
        ret['err-data'] = base64.b64decode(ret['err-data']) #.decode("GB2312")
    utils.print_dict(ret)
except :
    print "error"


