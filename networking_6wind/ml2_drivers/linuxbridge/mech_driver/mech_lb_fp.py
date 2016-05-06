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
from oslo_log import log

from networking_6wind.common import constants
from networking_6wind.common.utils import get_vif_vhostuser_socket

from neutron.agent import securitygroups_rpc
from neutron.extensions import portbindings
from neutron.plugins.ml2 import driver_api
from neutron.plugins.ml2.drivers.linuxbridge.mech_driver import (
    mech_linuxbridge)
from neutron.plugins.ml2.drivers.mech_agent import (
    SimpleAgentMechanismDriverBase)

LOG = log.getLogger(__name__)


class LBFPMechanismDriver(mech_linuxbridge.LinuxbridgeMechanismDriver):
    """Attach to networks using linuxbridge L2 agent.

    The OVSFPMechanismDriver integrates the ml2 plugin with the fast path
    linuxbridge L2 agent. Port binding with this driver requires the lb fp
    agent to be running on the port's host, and that agent to have connectivity
    to at least one segment of the port's network.
    """

    def __init__(self):
        agent_type = constants.AGENT_TYPE_LINUXBRIDGE_FP
        vif_type = portbindings.VIF_TYPE_BRIDGE
        sg_enabled = securitygroups_rpc.is_firewall_enabled()
        vif_details = {portbindings.CAP_PORT_FILTER: sg_enabled}

        SimpleAgentMechanismDriverBase.__init__(self, agent_type, vif_type,
                                                vif_details)

    def try_to_bind_segment_for_agent(self, context, segment, agent):
        if self.check_segment_for_agent(segment, agent):
            context.set_binding(segment[driver_api.ID],
                                get_vif_type(agent),
                                get_vif_details(agent, context))
            return True
        else:
            return False

    def get_vif_type(self, agent):
        agent_type = agent.agent_type

        if agent_type == constants.AGENT_TYPE_LINUXBRIDGE_FP:
            fp_offload = agent['configurations']['fp_offload']
            if fp_offload:
                return portbindings.VIF_TYPE_VHOST_USER

        return self.vif_type

    def get_vif_details(self, agent, context):
        agent_type = agent.agent_type

        if agent_type == constants.AGENT_TYPE_LINUXBRIDGE_FP:
            fp_offload = agent['configurations']['fp_offload']
            if fp_offload:
                vif_details_copy = self.vif_details.copy()
                vif_vhostuser_socket = get_vif_vhostuser_socket(context.current['id'])
                vif_details_copy[portbindings.VHOST_USER_SOCKET] = vif_vhostuser_socket
                vif_details_copy[portbindings.VHOST_USER_MODE] = portbindings.VHOST_USER_MODE_CLIENT
                vif_details_copy[constants.VIF_VHOSTUSER_FP_PLUG] = True
                return vif_details_copy

        return self.vif_details
