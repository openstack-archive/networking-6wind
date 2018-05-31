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
from oslo_config import cfg

from networking_6wind.common import constants
from networking_6wind.common.utils import get_vif_vhostuser_socket
from networking_6wind.ml2_drivers.openvswitch.mech_driver import mech_ovs_fp

from neutron.plugins.ml2.drivers.openvswitch.agent.common import (
    constants as a_const)
from neutron.tests.unit.plugins.ml2 import _test_mech_agent as base
from neutron.tests.unit.plugins.ml2.drivers.openvswitch.mech_driver import (
    test_mech_openvswitch as test_ovs)
from neutron_lib.api.definitions import portbindings

mode = portbindings.VHOST_USER_MODE_SERVER
socket = get_vif_vhostuser_socket(constants.VIF_VHOSTUSER_SOCKET_PREFIX,
                                  constants.VIF_VHOSTUSER_SOCKET_DIR,
                                  base.PORT_ID)
VIF_OVS = portbindings.VIF_TYPE_OVS


class OVSFPMechanismBaseTestCase(test_ovs.OpenvswitchMechanismBaseTestCase):
    VIF_TYPE = portbindings.VIF_TYPE_VHOST_USER

    VIF_BRIDGE = portbindings.VIF_TYPE_BRIDGE

    VIF_DETAILS = {portbindings.OVS_DATAPATH_TYPE: a_const.OVS_DATAPATH_SYSTEM,
                   portbindings.CAP_PORT_FILTER: False,
                   portbindings.OVS_HYBRID_PLUG: False,
                   constants.VIF_VHOSTUSER_FP_PLUG: True,
                   portbindings.VHOST_USER_OVS_PLUG: True,
                   portbindings.VHOST_USER_MODE: mode,
                   portbindings.VHOST_USER_SOCKET: socket}
    AGENT_TYPE = n_const.AGENT_TYPE_OVS

    GOOD_MAPPINGS = {'fake_physical_network': 'fake_bridge'}
    GOOD_TUNNEL_TYPES = ['gre', 'vxlan']
    GOOD_CONFIGS = {'bridge_mappings': GOOD_MAPPINGS,
                    'tunnel_types': GOOD_TUNNEL_TYPES}

    BAD_MAPPINGS = {'wrong_physical_network': 'wrong_bridge'}
    BAD_TUNNEL_TYPES = ['bad_tunnel_type']
    BAD_CONFIGS = {'bridge_mappings': BAD_MAPPINGS,
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
                   'host': 'bad_host_2',
                   'agent_type': AGENT_TYPE}]
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
        super(OVSFPMechanismBaseTestCase, self).setUp()
        self.driver = mech_ovs_fp.OVSFPMechanismDriver()
        self.driver.needs_update = False
        self.driver.fp_info = self.FP_INFO
        self.driver.initialize()


class OVSFPMechanismSGDisabledBaseTestCase(OVSFPMechanismBaseTestCase):
    VIF_DETAILS = {portbindings.OVS_DATAPATH_TYPE: a_const.OVS_DATAPATH_SYSTEM,
                   portbindings.CAP_PORT_FILTER: False,
                   portbindings.OVS_HYBRID_PLUG: False,
                   constants.VIF_VHOSTUSER_FP_PLUG: True,
                   portbindings.VHOST_USER_OVS_PLUG: True,
                   portbindings.VHOST_USER_MODE: mode,
                   portbindings.VHOST_USER_SOCKET: socket}

    def setUp(self):
        cfg.CONF.set_override('enable_security_group',
                              False,
                              group='SECURITYGROUP')
        super(OVSFPMechanismSGDisabledBaseTestCase, self).setUp()


class OVSFPMechanismGenericTestCase(OVSFPMechanismBaseTestCase,
                                    base.AgentMechanismGenericTestCase):
    pass


class OVSFPMechanismLocalTestCase(OVSFPMechanismBaseTestCase,
                                  base.AgentMechanismLocalTestCase):
    pass


class OVSFPMechanismFlatTestCase(OVSFPMechanismBaseTestCase,
                                 base.AgentMechanismFlatTestCase):
    pass


class OVSFPMechanismVlanTestCase(OVSFPMechanismBaseTestCase,
                                 base.AgentMechanismVlanTestCase):
    pass


class OVSFPMechanismGreTestCase(OVSFPMechanismBaseTestCase,
                                base.AgentMechanismGreTestCase):
    pass


class OVSFPMechanismSGDisabledLocalTestCase(
    OVSFPMechanismSGDisabledBaseTestCase,
    base.AgentMechanismLocalTestCase):
    pass
