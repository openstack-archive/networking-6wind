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


# -----------------------------------------------------------------------------
DEFAULT_VHOSTUSER_IFACENAME = 'tap_unused_%d'


class VhostUserPort(object):
    """A class to represent a vhostuser port"""

    def __init__(self, port_id, iface_name):
        """Create a VhostUserPort

        :arg int portid:
             DPDK portid of the vhostuser device on the hypervisor
        :arg str iface_name:
            Name of the vhostuser device on the hypervisor.
        """

        self.port_id = port_id
        self.iface_name = iface_name

# -----------------------------------------------------------------------------
FP_SHMEM_PORTS_RE = re.compile('port (?P<port_id>\d+):.*?(pmd-vhost).*'
                               ' (?P<iface>\S+)$')


def __get_available_vhostuser_port():
    """Use fp-shmem-port to get an available vhostuser port on the host

    :returns:
        a VhostUserPort object
    """
    try:
        out, err = execute('fp-shmem-ports', '-d', '-e', 'disabled',
                           '--driver', 'pmd-vhost', run_as_root=True)
    except processutils.ProcessExecutionError as exception:
        utils.log_exception('Failed to run fp-shem-ports -d', exception)
        return {}

    for match in FP_SHMEM_PORTS_RE.finditer(out):
        port_id = int(match.group('port_id'))
        iface_name = match.group('iface')

        return VhostUserPort(port_id=port_id, iface_name=iface_name)

    return None


def __get_used_vhostuser_port(iface_name):
    """Use fp-shmem-port to find a used vhostuser port from this ifname

    :arg str iface_name:
         Name of the interface of the vhostuser port to find
    :returns:
        a VhostUserPort object
    """
    try:
        out, err = execute('fp-shmem-ports', '-d', '-e', 'enabled',
                           '--driver', 'pmd-vhost', run_as_root=True)
    except processutils.ProcessExecutionError as exception:
        utils.log_exception('Failed to run fp-shem-ports -d', exception)
        return {}

    for match in FP_SHMEM_PORTS_RE.finditer(out):
        if match.group('iface') == iface_name:
            port_id = int(match.group('port_id'))
            iface_name = match.group('iface')

            return VhostUserPort(port_id=port_id, iface_name=iface_name)

    return None


# -----------------------------------------------------------------------------
def count_vhostuser_ports(select='all'):
    """Use fp-shmem-port to count the number of vhostuser ports on the host

    :arg str select:
         'all' to select all the vhostuser ports
         'enabled' to select all the enabled vhostuser ports
                   (i.e. port already used by a VM)
         'disabled' to select all the disabled vhostuser ports
                   (i.e. port available)
    """
    out = None
    try:
        out, err = utils.execute('fp-shmem-ports', '-c', '-e', select,
                                 '--driver', 'vhost-pmd', run_as_root=True)
    except processutils.ProcessExecutionError as exception:
        utils.log_exception('Failed to run fp-shem-ports -c', exception)
        return 0

    return int(out)


def get_vhostuser_port(new_iface, socket_path):
    """Get an available vhostuser port:

    :arg str new_iface:
    the iface name to set for the reserved vhostuser port
    :arg int nb_queues:
    number of queues to configure on the vhostuser port

    :returns:
    a vhostuser object if success or None if there is no available port
    """
    # first check if the interface is already configured
    vhostuser_port = __get_used_vhostuser_port(new_iface)
    if vhostuser_port:
        return vhostuser_port

    vhostuser_port = __get_available_vhostuser_port()
    if vhostuser_port is None:
        return None

    devargs = "sockmode=client,sockname=%s" % socket_path

    utils.set_down_iface(vhostuser_port.iface_name)
    utils.rename_iface(vhostuser_port.iface_name, new_iface)
    utils.enable_dpdk_port(vhostuser_port.port_id, 'all', devargs)
    utils.set_up_iface(new_iface)

    return vhostuser_port


def put_vhostuser_port(iface_name):
    """Put back a vhostuser port in the available pool used by a vm

    :arg str iface:
    the iface name of the vhostuser port to put back in the available pool

    """
    vhostuser_port = __get_used_vhostuser_port(iface_name)
    if vhostuser_port is None:
        return None

    # rename with default name
    utils.set_down_iface(vhostuser_port.iface_name)
    utils.disable_dpdk_port(vhostuser_port.port_id)
    new_iface_name = DEFAULT_VHOSTUSER_IFACENAME % vhostuser_port.port_id
    utils.rename_iface(vhostuser_port.iface_name, new_iface_name)
