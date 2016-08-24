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

from networking_6wind._i18n import _LE
from networking_6wind.common import constants

import nova.conf
from nova.network import linux_net
from nova.network import model
from nova import utils

from oslo_concurrency import processutils
from oslo_log import log as logging

CONF = nova.conf.CONF

LOG = logging.getLogger(__name__)

_plug_vhostuser_fp = None
_unplug_vhostuser_fp = None


def decorator(name, function):
    """Decorator for (un)plug_vhostuser_fp

    This function must be used with the monkey_patch_modules option in
    nova.conf

    Example:
    monkey_patch=true
    monkey_patch_modules=nova.virt.libvirt.vif:\
                 openstack_dpdk_vnic.kilo.nova.virt.libvirt.vif.decorator
    """

    global _plug_vhostuser_fp, _unplug_vhostuser_fp

    if name == (
        'nova.virt.libvirt.vif.LibvirtGenericVIFDriver.plug_vhostuser_fp'):
        _plug_vhostuser_fp = function
        return plug_vhostuser_fp
    elif name == (
        'nova.virt.libvirt.vif.LibvirtGenericVIFDriver.unplug_vhostuser_fp'):
        _unplug_vhostuser_fp = function
        return unplug_vhostuser_fp
    else:
        return function


def plug_vhostuser_fp(self, instance, vif):
    """Create and plug fp netdevice

    This method replaces the one in upstream nova to support BRIDGE and TAP
    plug
    """

    dev = self.get_vif_devname(vif)
    if linux_net.device_exists(dev):
        return

    fp_plug_type = vif['details'].get(constants.VIF_VHOSTUSER_FP_PLUG_TYPE,
                                      None)
    sockmode_qemu, sockpath = self._get_vhostuser_settings(vif)
    sockmode_port = 'client' if sockmode_qemu == 'server' else 'server'

    try:
        linux_net.create_fp_dev(dev, sockpath, sockmode_port)

        if fp_plug_type == 'ovs':
            bridge_name = vif['details'].get(model.VIF_DETAILS_BRIDGE_NAME,
                                             CONF.neutron.ovs_bridge)
            vif['network']['bridge'] = bridge_name

            if vif.is_hybrid_plug_enabled():
                self.plug_ovs_hybrid(instance, vif)
                utils.execute('brctl', 'addif',
                              self.get_br_name(vif['id']),
                              dev, run_as_root=True)
            else:
                iface_id = self.get_ovs_interfaceid(vif)
                mtu = vif['network'].get_meta('mtu')
                linux_net.create_ovs_vif_port(self.get_bridge_name(vif),
                                              dev, iface_id,
                                              vif['address'],
                                              instance.uuid, mtu)
        elif fp_plug_type == 'bridge':
            bridge_name = vif['details'].get(model.VIF_DETAILS_BRIDGE_NAME, "")
            utils.plug_bridge_vif_port(bridge_name, dev)
        elif fp_plug_type == 'tap':
            mac = vif['details'].get(model.VIF_DETAILS_TAP_MAC_ADDRESS)
            utils.execute('ip', 'link', 'set', dev, 'address', mac,
                          run_as_root=True, check_exit_code=[0, 2, 254])
    except processutils.ProcessExecutionError:
        LOG.exception(_LE('Failed while plugging vif'), instance=instance)


def unplug_vhostuser_fp(self, instance, vif):
    """Unplug and delete fp netdevice

    This method replaces the one in upstream nova to support BRIDGE unplug
    """

    dev = self.get_vif_devname(vif)
    fp_plug_type = vif['details'].get(constants.VIF_VHOSTUSER_FP_PLUG_TYPE,
                                      None)

    try:
        if fp_plug_type == 'ovs':
            bridge_name = vif['details'].get(model.VIF_DETAILS_BRIDGE_NAME,
                                             CONF.neutron.ovs_bridge)
            vif['network']['bridge'] = bridge_name

            if vif.is_hybrid_plug_enabled():
                self.unplug_ovs_hybrid(instance, vif)
            else:
                linux_net.delete_ovs_vif_port(self.get_bridge_name(vif),
                                              dev, False)
        elif fp_plug_type == 'bridge':
            bridge_name = vif['details'].get(model.VIF_DETAILS_BRIDGE_NAME, "")
            utils.unplug_bridge_vif_port(bridge_name, dev)
        linux_net.delete_fp_dev(dev)
    except processutils.ProcessExecutionError:
        LOG.exception(_LE("Failed while unplugging vif"), instance=instance)
