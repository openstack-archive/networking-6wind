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
from neutron_lib.api.definitions import portbindings
from neutron_lib import constants as n_constants
from neutron_lib.plugins.ml2 import api
from oslo_log import log

from networking_6wind.common import constants
from networking_6wind.common.utils import get_vif_vhostuser_socket
from neutron.plugins.ml2.drivers.openvswitch.mech_driver import (
    mech_openvswitch)

LOG = log.getLogger(__name__)


class OVSFPMechanismDriver(mech_openvswitch.OpenvswitchMechanismDriver):
    """Attach to networks using neutron-fastpath-agent L2 agent.

    The OVSFPMechanismDriver integrates Ml2Plugin class with
    neutron-fastpath-agent and neutron-openvswicth-agent. Port binding requires
    neutron-fastpath-agent and neutron-openvswicth-agent to be run on the
    port's host, and these agents should have connectivity to at least one
    segment of the port's network.
    """

    def __init__(self):
        super(OVSFPMechanismDriver, self).__init__()
        self.agent_type = constants.FP_AGENT_TYPE
        self.fp_info = None

    def _get_ovs_agent(self, context):
        ovs_agent = None
        for agent in context.host_agents(n_constants.AGENT_TYPE_OVS):
            if agent:
                return agent
        return ovs_agent

    def try_to_bind_segment_for_agent(self, context, segment, agent):
        ovs_agent = self._get_ovs_agent(context)
        if ovs_agent is None:
            LOG.error("Refusing to bind port %s due to dead "
                      "neutron-openvswitch-agent" % context.current['id'])
            return False
        # pass ovs_agent, because it contains supported tunnel type in its
        # 'configurations' dict
        if not self.check_segment_for_agent(segment, ovs_agent):
            return False
        LOG.debug("Trying to retrieve fp_info from %s..." % agent)
        self.fp_info = agent.get('configurations')
        if self.fp_info is None or not self.fp_info['active']:
            LOG.error("Can't retrieve fp_info")
            return False
        LOG.debug("Correctly retrieved fp_info: %s" % self.fp_info)
        if portbindings.VIF_TYPE_OVS not in self.fp_info['supported_plugs']:
            LOG.error("vif_type %s is not supported in ovs-fp ML2 mechanism "
                      " driver" % portbindings.VIF_TYPE_OVS)
            return False
        context.set_binding(segment[api.ID], portbindings.VIF_TYPE_VHOST_USER,
                            self.get_vif_details(context, agent, segment))
        return True

    def get_vif_details(self, context, agent, segment):
        socket_prefix = self.fp_info['vhostuser_socket_prefix']
        socket_dir = self.fp_info['vhostuser_socket_dir']
        socket = get_vif_vhostuser_socket(socket_prefix, socket_dir,
                                          context.current['id'])
        qemu_mode = portbindings.VHOST_USER_MODE_CLIENT
        if self.fp_info['vhostuser_socket_mode'] == 'client':
            qemu_mode = portbindings.VHOST_USER_MODE_SERVER
        self.vif_details = super(OVSFPMechanismDriver,
                                 self).get_vif_details(context, agent, segment)
        details_copy = self.vif_details.copy()
        details_copy[portbindings.VHOST_USER_SOCKET] = socket
        details_copy[portbindings.VHOST_USER_MODE] = qemu_mode
        details_copy[constants.VIF_VHOSTUSER_FP_PLUG] = True
        details_copy[portbindings.VHOST_USER_OVS_PLUG] = True
        return details_copy
