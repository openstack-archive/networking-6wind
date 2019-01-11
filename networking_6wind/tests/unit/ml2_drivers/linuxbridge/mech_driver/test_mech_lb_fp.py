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
from neutron_lib.api.definitions import portbindings
from neutron_lib import constants as n_const

from networking_6wind.common import constants
from networking_6wind.common.utils import get_vif_vhostuser_socket
from networking_6wind.ml2_drivers.linuxbridge.mech_driver import mech_lb_fp
from networking_6wind.tests.unit.ml2_drivers import _test_mech_agent as base

from neutron.tests.unit.plugins.ml2.drivers.linuxbridge.mech_driver import (
    test_mech_linuxbridge as test_lb)


class LBFPMechanismBaseTestCase(test_lb.LinuxbridgeMechanismBaseTestCase):
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
    AGENT_TYPE = constants.FP_AGENT_TYPE

    GOOD_MAPPINGS = {'fake_physical_network': 'fake_interface'}
    GOOD_TUNNEL_TYPES = ['gre', 'vxlan']
    GOOD_CONFIGS = {'bridge_mappings': GOOD_MAPPINGS,
                    'tunnel_types': GOOD_TUNNEL_TYPES}

    GOOD_FP_INFO = {
        'product': 'virtual-accelerator',
        'product_version': '4.0',
        'timestamp': constants.BASE_TIMESTAMP,
        'active': True,
        'vhostuser_socket_dir': constants.VIF_VHOSTUSER_SOCKET_DIR,
        'vhostuser_socket_prefix': constants.VIF_VHOSTUSER_SOCKET_PREFIX,
        'vhostuser_socket_mode': portbindings.VHOST_USER_MODE_CLIENT,
        'supported_plugs': [VIF_OVS, VIF_BRIDGE],
    }

    BAD_FP_INFO = {
        'product': 'unknown',
        'product_version': 'unknown',
        'timestamp': constants.BASE_TIMESTAMP,
        'active': False,
        'vhostuser_socket_dir': constants.VIF_VHOSTUSER_SOCKET_DIR,
        'vhostuser_socket_prefix': constants.VIF_VHOSTUSER_SOCKET_PREFIX,
        'vhostuser_socket_mode': portbindings.VHOST_USER_MODE_CLIENT,
        'supported_plugs': [VIF_OVS, VIF_BRIDGE],
    }

    AGENTS = [{'alive': True,
               'configurations': GOOD_FP_INFO,
               'host': 'host',
               'agent_type': AGENT_TYPE},
              {'alive': True,
               'configurations': GOOD_CONFIGS,
               'host': 'host',
               'agent_type': n_const.AGENT_TYPE_LINUXBRIDGE}]
    AGENTS_DEAD = [{'alive': False,
                    'configurations': GOOD_FP_INFO,
                    'host': 'dead_host',
                    'agent_type': AGENT_TYPE},
                   {'alive': False,
                    'configurations': GOOD_CONFIGS,
                    'host': 'host',
                    'agent_type': n_const.AGENT_TYPE_LINUXBRIDGE}]
    AGENTS_BAD = [{'alive': True,
                   'configurations': BAD_FP_INFO,
                   'host': 'bad_host_2',
                   'agent_type': AGENT_TYPE},
                  {'alive': True,
                   'configurations': GOOD_CONFIGS,
                   'host': 'bad_host_2',
                   'agent_type': n_const.AGENT_TYPE_LINUXBRIDGE}]

    def setUp(self):
        super(LBFPMechanismBaseTestCase, self).setUp()
        self.driver = mech_lb_fp.LBFPMechanismDriver()
        self.driver.fp_info = self.BAD_FP_INFO
        self.driver.initialize()


class LBFPMechanismGenericTestCase(LBFPMechanismBaseTestCase,
                                   base.FPMechanismGenericTestCase):
    pass


class LBFPMechanismLocalTestCase(LBFPMechanismBaseTestCase,
                                 base.FPMechanismLocalTestCase):
    pass


class LBFPMechanismFlatTestCase(LBFPMechanismBaseTestCase,
                                base.FPMechanismFlatTestCase):
    pass


class LBFPMechanismVlanTestCase(LBFPMechanismBaseTestCase,
                                base.FPMechanismVlanTestCase):
    pass


class LBFPMechanismGreTestCase(LBFPMechanismBaseTestCase,
                               base.FPMechanismVlanTestCase):
    pass
