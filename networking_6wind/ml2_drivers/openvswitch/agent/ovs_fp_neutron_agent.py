#    Copyright 2016 6WIND S.A.
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

import sys

from oslo_log import log as logging
from oslo_config import cfg

from networking_6wind.common import constants
from networking_6wind.common import utils

from neutron.plugins.ml2.drivers.openvswitch.agent import (
        prepare_xen_compute, validate_tunnel_config )
from neutron.plugins.ml2.drivers.openvswitch.agent import (
        ovs_neutron_agent as ovs_agent )


LOG = logging.getLogger(__name__)
cfg.CONF.import_group('AGENT', 'neutron.plugins.ml2.drivers.openvswitch.'
                      'agent.common.config')
cfg.CONF.import_group('OVS', 'neutron.plugins.ml2.drivers.openvswitch.agent.'
                      'common.config')

OVS_FP_AGENT_BINARY = 'neutron-openvswitch-fp-agent'


class OVSFPNeutronAgent(ovs_agent.OVSNeutronAgent):

    def __init__(self, bridge_classes, conf=None):
        super(OVSFPNeutronAgent, self).__init__(bridge_classes, conf);
        self.agent_state['agent_type'] = constants.AGENT_TYPE_OVS_FP
        self.agent_state['binary'] = OVS_FP_AGENT_BINARY

    def _report_state(self):
        self.agent_state['configurations']['fp_offload'] = utils.check_fp_offload()
        super(LinuxBridgeFPManager, self)._report_state()

# Copy from official ovs agent
def main(bridge_classes):
    prepare_xen_compute()
    validate_tunnel_config(cfg.CONF.AGENT.tunnel_types, cfg.CONF.OVS.local_ip)

    try:
        agent = OVSFPNeutronAgent(bridge_classes, cfg.CONF)
    except (RuntimeError, ValueError) as e:
        LOG.error(_LE("%s Agent terminated!"), e)
        sys.exit(1)
    agent.daemon_loop()
