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

from oslo_config import cfg

from networking_6wind.common import constants
from networking_6wind.common.utils import get_vif_vhostuser_socket
from networking_6wind.ml2_drivers.openvswitch.mech_driver import mech_ovs_fp

from neutron.extensions import portbindings
from neutron.tests.unit.plugins.ml2 import _test_mech_agent as base
from neutron.tests.unit.plugins.ml2.drivers.openvswitch.mech_driver import (
    test_mech_openvswitch as test_ovs)


class OVSFPMechanismBaseTestCase(test_ovs.OpenvswitchMechanismBaseTestCase):
    VIF_TYPE = constants.VIF_TYPE_VHOSTUSER
    VIF_DETAILS = {portbindings.CAP_PORT_FILTER: True,
                   portbindings.OVS_HYBRID_PLUG: True,
                   portbindings.VHOST_USER_OVS_PLUG: True,
                   constants.VIF_VHOSTUSER_OVS_TYPE: 'ovs-fp',
                   constants.VIF_VHOSTUSER_SOCKET: get_vif_vhostuser_socket(
                       base.PORT_ID)}

    def setUp(self):
        super(OVSFPMechanismBaseTestCase, self).setUp()
        self.driver = mech_ovs_fp.OVSFPMechanismDriver()
        self.driver.initialize()


class OVSFPMechanismSGDisabledBaseTestCase(
    OVSFPMechanismBaseTestCase):
    VIF_DETAILS = {portbindings.CAP_PORT_FILTER: False,
                   portbindings.OVS_HYBRID_PLUG: False,
                   portbindings.VHOST_USER_OVS_PLUG: True,
                   constants.VIF_VHOSTUSER_OVS_TYPE: 'ovs-fp',
                   constants.VIF_VHOSTUSER_SOCKET: get_vif_vhostuser_socket(
                       base.PORT_ID)}

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
