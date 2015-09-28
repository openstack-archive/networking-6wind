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

from nova.network import model
from nova import utils
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


# The following functions are used as monkey patches on the code defined in
# nova/virt/libvirt/vif.py

def plug_vhostuser(self, instance, vif):
    ovs_fp_plug = vif['details'].get(model.VIF_DETAILS_VHOSTUSER_OVS_PLUG,
                                     False)
    if ovs_fp_plug:
        iface_id = self.get_ovs_interfaceid(vif)
        port_name = vif['details'][model.VIF_DETAILS_VHOSTUSER_SOCKET]
        dev = self.get_vif_devname(vif)
        bridge_name = self.get_bridge_name(vif)

        utils.execute('vif-ovs-fp-plug', 'plug', vif['id'], vif['address'],
                      instance.uuid, port_name,
                      dev, iface_id, bridge_name,
                      vif.is_hybrid_plug_enabled(),
                      run_as_root=True)


def unplug_vhostuser(self, instance, vif):
    ovs_fp_plug = vif['details'].get(model.VIF_DETAILS_VHOSTUSER_OVS_PLUG,
                                     False)
    if ovs_fp_plug:
        iface_id = self.get_ovs_interfaceid(vif)
        port_name = vif['details'][model.VIF_DETAILS_VHOSTUSER_SOCKET]
        dev = self.get_vif_devname(vif)
        bridge_name = self.get_bridge_name(vif)

        utils.execute('vif-ovs-fp-plug', 'unplug', vif['id'], vif['address'],
                      instance.uuid, port_name,
                      dev, iface_id, bridge_name,
                      vif.is_hybrid_plug_enabled(),
                      run_as_root=True)
