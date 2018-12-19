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
from oslo_config import cfg
from oslo_log import log

from networking_6wind.common import constants
from networking_6wind.common.utils import get_vif_vhostuser_socket

from neutron.plugins.ml2.drivers.linuxbridge.mech_driver import (
    mech_linuxbridge)
from neutron_lib.api.definitions import portbindings
from neutron_lib.plugins.ml2 import api


LOG = log.getLogger(__name__)


class LBFPMechanismDriver(mech_linuxbridge.LinuxbridgeMechanismDriver):
    """Attach to networks using neutron-fastpath-agent L2 agent.

    The LBFPMechanismDriver integrates Ml2Plugin class with
    neutron-fastpath-agent.
    Port binding with this driver requires neutron-fastpath-agent to be run
    on the port's host, and that agent should have connectivity
    to at least one segment of the port's network.
    """

    def __init__(self):
        super(LBFPMechanismDriver, self).__init__()
        self.fp_info = {
            'timestamp': constants.BASE_TIMESTAMP,
            'product': 'unknown',
            'product_version': 'unknown',
            'active': False,
            'vhostuser_socket_dir': '',
            'vhostuser_socket_prefix': '',
            'vhostuser_socket_mode': '',
            'supported_plugs': [],
        }

    def _update_fp_info(self, context):
        LOG.debug('Trying to retrieve fp_info from agent...')
        for fp_agent in context.host_agents(constants.FP_AGENT_TYPE):
            LOG.debug("Checking agent: %s", fp_agent)
            self.fp_info = fp_agent['configurations']
            LOG.debug('Correctly retrieved fp_info from agent: %s' %
                      self.fp_info)

    def try_to_bind_segment_for_agent(self, context, segment, agent):
        if not self.check_segment_for_agent(segment, agent):
            return False
        self._update_fp_info(context)
        context.set_binding(segment[api.ID],
                            self.get_vif_type(context, agent, segment),
                            self.get_vif_details(context, agent, segment))
        return True

    def get_vif_type(self, context, agent, segment):
        if self.fp_info['active']:
            return portbindings.VIF_TYPE_VHOST_USER
        LOG.warning('virtual-accelerator is not alive, set %s vif_type'
                    % self.vif_type)
        return self.vif_type

    def get_vif_details(self, context, agent, segment):
        # fp-rte process is not alive -> call LinuxbridgeMechanismDriver.get_vif_details
        if not self.fp_info['active']:
            LOG.warning('virtual-accelerator is not alive, linuxbridge mechanism driver will be used')
            return self.vif_details
        # VIF TYPE is not supported -> call LinuxbridgeMechanismDriver.get_vif_details
        if portbindings.VIF_TYPE_BRIDGE not in self.fp_info['supported_plugs']:
            LOG.warning('VIF TYPE %s is not supported, linuxbridge mechanism driver will be used'
                        % portbindings.VIF_TYPE_BRIDGE)
            return self.vif_details
        socket_prefix = self.fp_info['vhostuser_socket_prefix']
        socket_dir = self.fp_info['vhostuser_socket_dir']
        socket = get_vif_vhostuser_socket(socket_prefix, socket_dir,
                                          context.current['id'])
        brg = constants.BRIDGE_PREFIX + context.network.current['id']

        if self.fp_info['vhostuser_socket_mode'] == 'client':
            qemu_mode = portbindings.VHOST_USER_MODE_SERVER
        else:
            qemu_mode = portbindings.VHOST_USER_MODE_CLIENT

        details_copy = self.vif_details.copy()
        details_copy[portbindings.VHOST_USER_SOCKET] = socket
        details_copy[portbindings.VHOST_USER_MODE] = qemu_mode
        details_copy[constants.VIF_VHOSTUSER_FP_PLUG] = True

        # Workaroud to notify nova of bridge name to be used during
        # plug. This should not be necessary because Nova can detect
        # this bridge name, but some code is missing for the
        # VIF_VHOSTUSER_FP_PLUG case (in nova/network/neutronv2/api.py)
        details_copy[portbindings.VIF_DETAILS_BRIDGE_NAME] = brg
        return details_copy
