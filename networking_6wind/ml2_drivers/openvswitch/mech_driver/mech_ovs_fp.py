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
from neutron.common import constants as n_constants
from neutron.extensions import portbindings
from neutron.plugins.ml2 import driver_api
from neutron.plugins.ml2.drivers.mech_agent import (
    SimpleAgentMechanismDriverBase)
from neutron.plugins.ml2.drivers.openvswitch.mech_driver import (
    mech_openvswitch)

LOG = log.getLogger(__name__)


class OVSFPMechanismDriver(mech_openvswitch.OpenvswitchMechanismDriver):
    """Attach to networks using openvswitch L2 agent.

    The OVSFPMechanismDriver integrates the ml2 plugin with the fast path
    openvswitch L2 agent. Port binding with this driver requires the ovs fp
    agent to be running on the port's host, and that agent to have connectivity
    to at least one segment of the port's network.
    """

    def __init__(self):
        sg_enabled = securitygroups_rpc.is_firewall_enabled()
        vif_details = {portbindings.CAP_PORT_FILTER: sg_enabled,
                       portbindings.OVS_HYBRID_PLUG: sg_enabled,
                       portbindings.VHOST_USER_OVS_PLUG: True,
                       constants.VIF_VHOSTUSER_OVS_TYPE: 'ovs-fp'}

        SimpleAgentMechanismDriverBase.__init__(self,
                                                n_constants.AGENT_TYPE_OVS,
                                                constants.VIF_TYPE_VHOSTUSER,
                                                vif_details)

    def try_to_bind_segment_for_agent(self, context, segment, agent):
        if self.check_segment_for_agent(segment, agent):
            context.set_binding(segment[driver_api.ID], self.vif_type,
                                self._get_vif_details(context))
            return True
        else:
            return False

    def _get_vif_details(self, context):
        vif_details = self.vif_details.copy()
        vif_vhostuser_socket = get_vif_vhostuser_socket(context.current['id'])
        vif_details[constants.VIF_VHOSTUSER_SOCKET] = vif_vhostuser_socket
        return vif_details
