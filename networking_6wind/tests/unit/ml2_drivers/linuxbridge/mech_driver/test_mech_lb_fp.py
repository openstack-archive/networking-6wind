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

from networking_6wind.common import constants
from networking_6wind.common.utils import get_vif_vhostuser_socket
from networking_6wind.ml2_drivers.linuxbridge.mech_driver import mech_lb_fp

from neutron.extensions import portbindings
from neutron.tests.unit.plugins.ml2 import _test_mech_agent as base


class LBFPMechanismBaseTestCase(base.AgentMechanismBaseTestCase):
    VIF_TYPE = portbindings.VIF_TYPE_VHOST_USER
    AGENT_TYPE = constants.AGENT_TYPE_LINUXBRIDGE_FP
    VIF_DETAILS = {portbindings.CAP_PORT_FILTER: True,
                   constants.VIF_VHOSTUSER_FP_PLUG: True,
                   portbindings.VHOST_USER_SOCKET: get_vif_vhostuser_socket(
                       base.PORT_ID)}

    GOOD_MAPPINGS = {'fake_physical_network': 'fake_interface'}
    GOOD_TUNNEL_TYPES = ['gre', 'vxlan']
    GOOD_CONFIGS = {'interface_mappings': GOOD_MAPPINGS,
                    'tunnel_types': GOOD_TUNNEL_TYPES,
                    'fp_offload': True}

    BAD_MAPPINGS = {'wrong_physical_network': 'wrong_interface'}
    BAD_TUNNEL_TYPES = ['bad_tunnel_type']
    BAD_CONFIGS = {'interface_mappings': BAD_MAPPINGS,
                   'tunnel_types': BAD_TUNNEL_TYPES,
                   'fp_offload': False}

    AGENTS = [{'alive': True,
               'configurations': GOOD_CONFIGS,
               'host': 'host'}]
    AGENTS_DEAD = [{'alive': False,
                    'configurations': GOOD_CONFIGS,
                    'host': 'dead_host'}]
    AGENTS_BAD = [{'alive': False,
                   'configurations': GOOD_CONFIGS,
                   'host': 'bad_host_1'},
                  {'alive': True,
                   'configurations': BAD_CONFIGS,
                   'host': 'bad_host_2'}]

    def setUp(self):
        super(LBFPMechanismBaseTestCase, self).setUp()
        self.driver = mech_lb_fp.LBFPMechanismDriver()
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
