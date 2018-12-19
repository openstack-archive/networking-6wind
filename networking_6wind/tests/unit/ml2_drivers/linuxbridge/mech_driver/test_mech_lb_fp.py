# Copyright 2015 6WIND S.A.
# All Rights Reserved.
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

from neutron_lib import constants as n_const

from networking_6wind.common import constants
from networking_6wind.common.utils import get_vif_vhostuser_socket
from networking_6wind.ml2_drivers.linuxbridge.mech_driver import mech_lb_fp

from neutron.tests.unit.plugins.ml2 import _test_mech_agent as base
from neutron_lib.api.definitions import portbindings


class LBFPMechanismBaseTestCase(base.AgentMechanismBaseTestCase):
    mode = portbindings.VHOST_USER_MODE_SERVER
    socket = get_vif_vhostuser_socket(constants.VIF_VHOSTUSER_SOCKET_PREFIX,
                                      constants.VIF_VHOSTUSER_SOCKET_DIR,
                                      base.PORT_ID)
    br_name = constants.BRIDGE_PREFIX + base.NETWORK_ID

    VIF_TYPE = portbindings.VIF_TYPE_VHOST_USER

    VIF_BRIDGE = portbindings.VIF_TYPE_BRIDGE
    VIF_OVS = portbindings.VIF_TYPE_OVS

    VIF_DETAILS = {portbindings.CAP_PORT_FILTER: True,
                   constants.VIF_VHOSTUSER_FP_PLUG: True,
                   portbindings.VHOST_USER_MODE: mode,
                   portbindings.VHOST_USER_SOCKET: socket,
                   portbindings.VIF_DETAILS_BRIDGE_NAME: br_name}
    AGENT_TYPE = n_const.AGENT_TYPE_LINUXBRIDGE

    GOOD_MAPPINGS = {'fake_physical_network': 'fake_interface'}
    GOOD_TUNNEL_TYPES = ['gre', 'vxlan']
    GOOD_CONFIGS = {'interface_mappings': GOOD_MAPPINGS,
                    'tunnel_types': GOOD_TUNNEL_TYPES}

    BAD_MAPPINGS = {'wrong_physical_network': 'wrong_interface'}
    BAD_TUNNEL_TYPES = ['bad_tunnel_type']
    BAD_CONFIGS = {'interface_mappings': BAD_MAPPINGS,
                   'tunnel_types': BAD_TUNNEL_TYPES}

    AGENTS = [{'alive': True,
               'configurations': GOOD_CONFIGS,
               'host': 'host',
               'agent_type': AGENT_TYPE}]
    AGENTS_DEAD = [{'alive': False,
                    'configurations': GOOD_CONFIGS,
                    'host': 'dead_host',
                    'agent_type': AGENT_TYPE}]
    AGENTS_BAD = [{'alive': False,
                   'configurations': GOOD_CONFIGS,
                   'host': 'bad_host_1',
                   'agent_type': AGENT_TYPE},
                  {'alive': True,
                   'configurations': BAD_CONFIGS,
                   'host': 'bad_host_2'}]
    FP_INFO = {
        'product': 'unknown',
        'product_version': 'unknown',
        'timestamp': constants.BASE_TIMESTAMP,
        'active': True,
        'vhostuser_socket_dir': constants.VIF_VHOSTUSER_SOCKET_DIR,
        'vhostuser_socket_prefix': constants.VIF_VHOSTUSER_SOCKET_PREFIX,
        'vhostuser_socket_mode': portbindings.VHOST_USER_MODE_CLIENT,
        'supported_plugs': [VIF_OVS, VIF_BRIDGE],
    }

    def setUp(self):
        super(LBFPMechanismBaseTestCase, self).setUp()
        self.driver = mech_lb_fp.LBFPMechanismDriver()
        self.driver.fp_info = self.FP_INFO
        self.driver.initialize()


class LBFPMechanismGenericTestCase(LBFPMechanismBaseTestCase,
                                   base.AgentMechanismGenericTestCase):
    pass


class LBFPMechanismLocalTestCase(LBFPMechanismBaseTestCase,
                                 base.AgentMechanismLocalTestCase):
    pass


class LBFPMechanismFlatTestCase(LBFPMechanismBaseTestCase,
                                base.AgentMechanismFlatTestCase):
    pass


class LBFPMechanismVlanTestCase(LBFPMechanismBaseTestCase,
                                base.AgentMechanismVlanTestCase):
    pass


class LBFPMechanismGreTestCase(LBFPMechanismBaseTestCase,
                               base.AgentMechanismGreTestCase):
    pass
