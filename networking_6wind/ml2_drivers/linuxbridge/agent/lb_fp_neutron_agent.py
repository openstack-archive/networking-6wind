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

import sys

from oslo_config import cfg
from oslo_log import log as logging
from oslo_service import service

from networking_6wind.common import constants
from networking_6wind.common import utils

from neutron.common import config as common_config
from neutron.common import utils as n_utils
from neutron.i18n import _LE
from neutron.i18n import _LI
from neutron.plugins.ml2.drivers.linuxbridge.agent import (
    linuxbridge_neutron_agent as lb_agent)


LOG = logging.getLogger(__name__)


class LBFPNeutronAgentRPC(lb_agent.LinuxBridgeNeutronAgentRPC):
    def __init__(self, bridge_mappings, interface_mappings, fp_offload,
                 polling_interval, quitting_rpc_timeout):
            super(LBFPNeutronAgentRPC, self).__init__(bridge_mappings,
                                                      interface_mappings,
                                                      polling_interval,
                                                      quitting_rpc_timeout)
            self.fp_offload = fp_offload

    def _report_state(self):
        self.agent_state['agent_type'] = constants.AGENT_TYPE_LINUXBRIDGE_FP
        self.agent_state['configurations']['fp_offload'] = self.fp_offload
        super(LBFPNeutronAgentRPC, self)._report_state()


# Copy from official linux bridge agent
def main():
    common_config.init(sys.argv[1:])

    common_config.setup_logging()
    try:
        interface_mappings = n_utils.parse_mappings(
            cfg.CONF.LINUX_BRIDGE.physical_interface_mappings)
    except ValueError as e:
        LOG.error(_LE("Parsing physical_interface_mappings failed: %s. "
                      "Agent terminated!"), e)
        sys.exit(1)
    LOG.info(_LI("Interface mappings: %s"), interface_mappings)

    try:
        bridge_mappings = n_utils.parse_mappings(
            cfg.CONF.LINUX_BRIDGE.bridge_mappings)
    except ValueError as e:
        LOG.error(_LE("Parsing bridge_mappings failed: %s. "
                      "Agent terminated!"), e)
        sys.exit(1)
    LOG.info(_LI("Bridge mappings: %s"), bridge_mappings)

    polling_interval = cfg.CONF.AGENT.polling_interval
    quitting_rpc_timeout = cfg.CONF.AGENT.quitting_rpc_timeout
    agent = LBFPNeutronAgentRPC(bridge_mappings,
                                interface_mappings,
                                utils.check_fp_offload(),
                                polling_interval,
                                quitting_rpc_timeout)
    LOG.info(_LI("Agent initialized successfully, now running... "))
    launcher = service.launch(cfg.CONF, agent)
    launcher.wait()


if __name__ == "__main__":
    main()
