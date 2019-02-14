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
from oslo_config import cfg

from networking_6wind.common import constants
from networking_6wind.common.utils import get_socket_path
from networking_6wind.ml2_drivers.openvswitch.mech_driver import mech_ovs_fp
from networking_6wind.tests.unit.ml2_drivers import _test_mech_agent as base

from neutron.plugins.ml2.drivers.openvswitch.agent.common import (
    constants as a_const)
from neutron.tests.unit.plugins.ml2.drivers.openvswitch.mech_driver import (
    test_mech_openvswitch as test_ovs)

mode = portbindings.VHOST_USER_MODE_SERVER
socket = get_socket_path(constants.VHOSTUSER_SOCKET_PREFIX,
                         constants.VHOSTUSER_SOCKET_DIR, base.PORT_ID)


class OVSFPMechanismBaseTestCase(test_ovs.OpenvswitchMechanismBaseTestCase):
    VIF_TYPE = portbindings.VIF_TYPE_VHOST_USER

    VIF_OVS = portbindings.VIF_TYPE_OVS
    VIF_BRIDGE = portbindings.VIF_TYPE_BRIDGE
    VIF_TAP = portbindings.VIF_TYPE_TAP

    VIF_DETAILS = {portbindings.OVS_DATAPATH_TYPE: a_const.OVS_DATAPATH_SYSTEM,
                   portbindings.CAP_PORT_FILTER: True,
                   portbindings.OVS_HYBRID_PLUG: True,
                   constants.VIF_DETAILS_VHOSTUSER_FP_PLUG: True,
                   portbindings.VHOST_USER_OVS_PLUG: True,
                   portbindings.VHOST_USER_MODE: mode,
                   portbindings.VHOST_USER_SOCKET: socket}
    AGENT_TYPE = constants.FP_AGENT_TYPE

    GOOD_MAPPINGS = {'fake_physical_network': 'fake_bridge'}
    GOOD_TUNNEL_TYPES = ['gre', 'vxlan']
    GOOD_CONFIGS = {'bridge_mappings': GOOD_MAPPINGS,
                    'tunnel_types': GOOD_TUNNEL_TYPES}

    GOOD_FP_INFO = {
        'product': 'virtual-accelerator',
        'product_version': '4.0',
        'timestamp': constants.BASE_TIMESTAMP,
        'active': True,
        'vhostuser_socket_dir': constants.VHOSTUSER_SOCKET_DIR,
        'vhostuser_socket_prefix': constants.VHOSTUSER_SOCKET_PREFIX,
        'vhostuser_socket_mode': portbindings.VHOST_USER_MODE_CLIENT,
        'supported_plugs': [VIF_OVS, VIF_BRIDGE],
    }

    BAD_FP_INFO = {
        'product': 'unknown',
        'product_version': 'unknown',
        'timestamp': constants.BASE_TIMESTAMP,
        'active': False,
        'vhostuser_socket_dir': constants.VHOSTUSER_SOCKET_DIR,
        'vhostuser_socket_prefix': constants.VHOSTUSER_SOCKET_PREFIX,
        'vhostuser_socket_mode': portbindings.VHOST_USER_MODE_CLIENT,
        'supported_plugs': [VIF_OVS, VIF_BRIDGE, VIF_TAP],
    }

    AGENTS = [{'alive': True,
               'configurations': GOOD_FP_INFO,
               'host': 'host',
               'agent_type': AGENT_TYPE},
              {'alive': True,
               'configurations': GOOD_CONFIGS,
               'host': 'host',
               'agent_type': n_const.AGENT_TYPE_OVS}]
    AGENTS_DEAD = [{'alive': False,
                    'configurations': GOOD_FP_INFO,
                    'host': 'host',
                    'agent_type': AGENT_TYPE},
                   {'alive': False,
                    'configurations': GOOD_CONFIGS,
                    'host': 'host',
                    'agent_type': n_const.AGENT_TYPE_OVS}]
    AGENTS_BAD = [{'alive': True,
                   'configurations': BAD_FP_INFO,
                   'host': 'bad_host_2',
                   'agent_type': AGENT_TYPE},
                  {'alive': True,
                   'configurations': GOOD_CONFIGS,
                   'host': 'bad_host_2',
                   'agent_type': n_const.AGENT_TYPE_OVS}]

    def setUp(self):
        super(OVSFPMechanismBaseTestCase, self).setUp()
        self.driver = mech_ovs_fp.OVSFPMechanismDriver()
        self.driver.fp_info = self.BAD_FP_INFO
        self.driver.initialize()


class OVSFPMechanismSGDisabledBaseTestCase(OVSFPMechanismBaseTestCase):
    VIF_DETAILS = {portbindings.OVS_DATAPATH_TYPE: a_const.OVS_DATAPATH_SYSTEM,
                   portbindings.CAP_PORT_FILTER: False,
                   portbindings.OVS_HYBRID_PLUG: False,
                   constants.VIF_DETAILS_VHOSTUSER_FP_PLUG: True,
                   portbindings.VHOST_USER_OVS_PLUG: True,
                   portbindings.VHOST_USER_MODE: mode,
                   portbindings.VHOST_USER_SOCKET: socket}

    def setUp(self):
        cfg.CONF.set_override('enable_security_group',
                              False,
                              group='SECURITYGROUP')
        super(OVSFPMechanismSGDisabledBaseTestCase, self).setUp()


class OVSFPMechanismGenericTestCase(OVSFPMechanismBaseTestCase,
                                    base.FPMechanismGenericTestCase):
    pass


class OVSFPMechanismLocalTestCase(OVSFPMechanismBaseTestCase,
                                  base.FPMechanismLocalTestCase):
    pass


class OVSFPMechanismFlatTestCase(OVSFPMechanismBaseTestCase,
                                 base.FPMechanismFlatTestCase):
    pass


class OVSFPMechanismVlanTestCase(OVSFPMechanismBaseTestCase,
                                 base.FPMechanismVlanTestCase):
    pass


class OVSFPMechanismGreTestCase(OVSFPMechanismBaseTestCase,
                                base.FPMechanismGreTestCase):
    pass


class OVSFPMechanismSGDisabledLocalTestCase(
    OVSFPMechanismSGDisabledBaseTestCase,
    base.FPMechanismLocalTestCase):
    pass
