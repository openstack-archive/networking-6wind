#    Copyright 2015 6WIND S.A.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Misc utility functions
"""
from __future__ import print_function

import os

from nova.utils import execute


# -----------------------------------------------------------------------------
# misc
def log_exception(msg, exception):
    print ('Error: ', msg)
    print ('exception catched: %s', exception)

# -----------------------------------------------------------------------------
# linux net utils
NIC_NAME_LEN = 14


def device_exists(device):
    """Check if ethernet device exists."""
    return os.path.exists('/sys/class/net/%s' % device)


def delete_net_dev(dev):
    if device_exists(dev):
        execute('ip', 'link', 'delete', dev, run_as_root=True)


def create_veth_pair(dev1_name, dev2_name):
    execute('ip', 'link', 'add', dev1_name, 'type', 'veth', 'peer',
            'name', dev2_name, run_as_root=True)
    for dev in [dev1_name, dev2_name]:
        execute('ip', 'link', 'set', dev, 'up', run_as_root=True)
        execute('ip', 'link', 'set', dev, 'promisc', 'on', run_as_root=True)


def is_device_on_bridge(device_name):
    bridge_port_path = "/sys/devices/virtual/net/%s/brport" % (device_name)
    return os.path.exists(bridge_port_path)


def plug_ovs_vif_port(bridge, dev, iface_id, mac, instance_id):
    cmd = ['ovs-vsctl', '--timeout=120', '--', '--if-exists', 'del-port',
           dev, '--', 'add-port', bridge, dev,
           '--', 'set', 'Interface', dev,
           'external-ids:iface-id=%s' % iface_id,
           'external-ids:iface-status=active',
           'external-ids:attached-mac=%s' % mac,
           'external-ids:vm-uuid=%s' % instance_id]
    execute(*cmd, run_as_root=True)


def unplug_ovs_vif_port(bridge, dev):
    execute('ovs-vsctl', '--timeout=120', '--', '--if-exists', 'del-port',
            bridge, dev, run_as_root=True)


def set_down_iface(ifname):
    execute('ip', 'link', 'set', ifname, 'down', run_as_root=True)


def set_up_iface(ifname):
    execute('ip', 'link', 'set', ifname, 'up', run_as_root=True)

# -----------------------------------------------------------------------------
# dpdk fast path utils

def new_dpdk_virtual_port(driver, devargs, ifname):
    execute('fp-cli', 'new-virtual-port', driver, 'devargs', devargs, 'ifname',
            ifname, run_as_root=True)

def free_dpdk_port(ifname):
    execute('fp-cli', 'free-port', ifname, run_as_root=True)
