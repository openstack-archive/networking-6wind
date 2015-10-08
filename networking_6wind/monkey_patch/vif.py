# Copyright 2015 6WIND S.A.
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
Extented support of vif drivers
"""

from networking_6wind.common import constants

from nova import exception
from nova.i18n import _LE
from nova.network import linux_net
from nova.network import model
from nova import utils

from oslo_concurrency import processutils
from oslo_log import log as logging


LOG = logging.getLogger(__name__)

_plug_vhostuser = None
_unplug_vhostuser = None


def decorator(name, function):
    """This function must be used with the monkey_patch_modules option in nova.conf

    Example:
    monkey_patch=true
    monkey_patch_modules=nova.virt.libvirt.vif:\
                 openstack_dpdk_vnic.kilo.nova.virt.libvirt.vif.decorator
    """
    global _plug_vhostuser, _unplug_vhostuser

    if name == 'nova.virt.libvirt.vif.LibvirtGenericVIFDriver.plug_vhostuser':
        _plug_vhostuser = function
        return plug_vhostuser
    elif name == (
        'nova.virt.libvirt.vif.LibvirtGenericVIFDriver.unplug_vhostuser'):
        _unplug_vhostuser = function
        return unplug_vhostuser
    else:
        return function


def create_fp_vif_port(dev, driver, devargs):
    if not linux_net.device_exists(dev):
        utils.execute('fp-cli', 'new-virtual-port', driver, 'devargs',
                      devargs, 'ifname', dev, run_as_root=True)
    linux_net._set_device_mtu(dev)
    utils.execute('ip', 'link', 'set', dev, 'up', run_as_root=True,
                  check_exit_code=[0, 2, 254])


def _get_vhostuser_settings(self, vif):
    vif_details = vif['details']
    mode = vif_details.get(model.VIF_DETAILS_VHOSTUSER_MODE, 'server')
    sock_path = vif_details.get(model.VIF_DETAILS_VHOSTUSER_SOCKET)
    if sock_path is None:
        raise exception.VifDetailsMissingVhostuserSockPath(vif_id=vif['id'])
    return mode, sock_path


def plug_vhostuser_ovs_fp(self, instance, vif):
    """Plug ovs fp vhostuser port"""
    dev = self.get_vif_devname(vif)
    if linux_net.device_exists(dev):
        return

    sockmode_qemu, sockname = _get_vhostuser_settings(self, vif)
    sockmode_port = 'client' if sockmode_qemu == 'server' else 'server'
    devargs = 'sockname=%s,sockmode=%s' % (sockname, sockmode_port)

    try:
        create_fp_vif_port(dev, 'pmd-vhost', devargs)
        if vif.is_hybrid_plug_enabled():
            self.plug_ovs_hybrid(instance, vif)
            utils.execute('brctl', 'addif', self.get_br_name(vif['id']),
                          dev, run_as_root=True)
        else:
            iface_id = self.get_ovs_interfaceid(vif)
            linux_net.create_ovs_vif_port(self.get_bridge_name(vif),
                                          dev, iface_id, vif['address'],
                                          instance.uuid)
    except processutils.ProcessExecutionError:
        LOG.exception(_LE("Failed while plugging vif"), instance=instance)


def unplug_vhostuser_ovs_fp(self, instance, vif):
    """Unplug ovs fp vhostuser port"""
    dev = self.get_vif_devname(vif)
    if vif.is_hybrid_plug_enabled():
        self.unplug_ovs_hybrid(instance, vif)
        linux_net.delete_net_dev(dev)
    else:
        linux_net.delete_ovs_vif_port(self.get_bridge_name(vif), dev)


# The following functions are used as monkey patches on the code defined in
# nova/virt/libvirt/vif.py

def plug_vhostuser(self, instance, vif):
    ovs_plug = vif['details'].get(model.VIF_DETAILS_VHOSTUSER_OVS_PLUG,
                                  False)
    ovs_type = vif['details'].get(constants.VIF_VHOSTUSER_OVS_TYPE,
                                  "ovs-dpdk")

    if ovs_plug is True and ovs_type == 'ovs-fp':
        plug_vhostuser_ovs_fp(self, instance, vif)
    else:
        _plug_vhostuser(self, instance, vif)


def unplug_vhostuser(self, instance, vif):
    ovs_plug = vif['details'].get(model.VIF_DETAILS_VHOSTUSER_OVS_PLUG,
                                  False)
    ovs_type = vif['details'].get(constants.VIF_VHOSTUSER_OVS_TYPE,
                                  "ovs-dpdk")

    if ovs_plug is True and ovs_type == 'ovs-fp':
        unplug_vhostuser_ovs_fp(self, instance, vif)
    else:
        _unplug_vhostuser(self, instance, vif)
