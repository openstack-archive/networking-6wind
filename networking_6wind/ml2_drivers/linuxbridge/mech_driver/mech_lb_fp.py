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

import datetime

from networking_6wind.common import constants
from networking_6wind.common.utils import get_vif_vhostuser_socket

from neutron.plugins.ml2.drivers.linuxbridge.mech_driver import (
    mech_linuxbridge)
from neutron_lib.api.definitions import portbindings
from neutron_lib.plugins.ml2 import api


LOG = log.getLogger(__name__)
cfg.CONF.import_group('ml2_fp', 'networking_6wind.common.config')


class LBFPMechanismDriver(mech_linuxbridge.LinuxbridgeMechanismDriver):
    """Attach to networks using linuxbridge L2 agent.

    The OVSFPMechanismDriver integrates the ml2 plugin with the fast path
    linuxbridge L2 agent. Port binding with this driver requires the lb fp
    agent to be running on the port's host, and that agent to have connectivity
    to at least one segment of the port's network.
    """

    def __init__(self):
        super(LBFPMechanismDriver, self).__init__()

        self.conf = cfg.CONF.ml2_fp
        self.fp_info_max_age = self.conf.fp_info_max_age
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
        self.is_first_update = True
        self.needs_update = True

    def _update_fp_info(self, context):
        LOG.debug('Trying to retrieve fp_info from agent...')
        for fp_agent in context.host_agents(constants.FP_AGENT_TYPE):
            LOG.debug("Checking agent: %s", fp_agent)
            self.fp_info = fp_agent['configurations']
            LOG.debug('Correctly retrieved fp_info from agent: %s' %
                      self.fp_info)
            return

        self.fp_info = None

    def _get_fp_info(self, context):
        if self.fp_info is None:
            return

        ts_format = "%Y-%m-%d %H:%M:%S"
        current_time = datetime.datetime.now().strftime(ts_format)
        last_update = self.fp_info['timestamp']

        t1 = datetime.datetime.strptime(current_time, ts_format)
        t2 = datetime.datetime.strptime(last_update, ts_format)

        tdelta = t1 - t2
        age = tdelta.total_seconds()

        if age >= self.fp_info_max_age:
            self._update_fp_info(context)

    def try_to_bind_segment_for_agent(self, context, segment, agent):
        if self.needs_update:
            if self.is_first_update:
                self._update_fp_info(context)
                self.is_first_update = False
            else:
                self._get_fp_info(context)

        if self.check_segment_for_agent(segment, agent):
            context.set_binding(segment[api.ID],
                                self.get_vif_type(agent),
                                self.get_vif_details(agent, context))
            return True
        else:
            return False

    def get_vif_type(self, agent):
        if self.fp_info is not None and self.fp_info['active']:
            return portbindings.VIF_TYPE_VHOST_USER

        return self.vif_type

    def get_vif_details(self, agent, context):
        VIF_BRIDGE = portbindings.VIF_TYPE_BRIDGE
        if self.fp_info is not None and self.fp_info['active']:
            if VIF_BRIDGE in self.fp_info['supported_plugs']:
                socket_prefix = self.fp_info['vhostuser_socket_prefix']
                socket_dir = self.fp_info['vhostuser_socket_dir']
                socket = get_vif_vhostuser_socket(socket_prefix,
                                                  socket_dir,
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

        return self.vif_details
