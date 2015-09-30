#    Copyright 2014 6WIND S.A.
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
Set of functions to reserve/unreserve/configure vhostuser interfaces for a VM.
"""

import re

from oslo_concurrency import processutils

from nova.utils import execute

from networking_6wind.plug_scripts import utils

def create_vhostuser_port(iface_name, socket_path):
    """Create a new vhostuser port:

    :arg str iface_name:
    the iface name of the vhostuser port to create
    :arg str socket_path:
    the vhostuser socket path
    :returns:
    a vhostuser object if success or None if there is no available port
    """
    devargs = "sockmode=client,sockname=%s" % socket_path

    if not utils.device_exists(iface_name):
        utils.new_dpdk_virtual_port('pmd-vhost', devargs, iface_name)
        utils.set_up_iface(iface_name)

def delete_vhostuser_port(iface_name):
    """Delete a vhostuser port

    :arg str iface_name:
    the iface name of the vhostuser port to delete
    """
    if utils.device_exists(iface_name):
        utils.set_down_iface(iface_name)
        utils.free_dpdk_port(iface_name)
