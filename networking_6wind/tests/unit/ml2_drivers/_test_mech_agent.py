# Copyright 2019 6WIND S.A.
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

from neutron.tests.unit.plugins.ml2 import _test_mech_agent as base
from neutron_lib.api.definitions import portbindings

NETWORK_ID = "fake_network"
PORT_ID = "fake_port"


class FPPortContext(base.FakePortContext):
    def __init__(self, agent_type, agents, segments,
                 vnic_type=portbindings.VNIC_NORMAL,
                 original=None, profile=None):
        super(FPPortContext, self).__init__(agent_type, agents, segments,
                                            vnic_type, original, profile)

    def host_agents(self, agent_type):
        return [agent for agent in self._agents if agent_type in
                agent.get('agent_type') and agent.get('alive')]


class FPMechanismGenericTestCase(base.AgentMechanismGenericTestCase):
    def test_unknown_type(self):
        context = FPPortContext(self.AGENT_TYPE,
                                self.AGENTS,
                                self.UNKNOWN_TYPE_SEGMENTS,
                                vnic_type=self.VNIC_TYPE)
        self.driver.bind_port(context)
        self._check_unbound(context)


class FPMechanismLocalTestCase(base.AgentMechanismLocalTestCase):
    def test_type_local(self):
        context = FPPortContext(self.AGENT_TYPE,
                                self.AGENTS,
                                self.LOCAL_SEGMENTS,
                                vnic_type=self.VNIC_TYPE)
        self.driver.bind_port(context)
        self._check_bound(context, self.LOCAL_SEGMENTS[1])

    def test_type_local_dead(self):
        context = FPPortContext(self.AGENT_TYPE,
                                self.AGENTS_DEAD,
                                self.LOCAL_SEGMENTS,
                                vnic_type=self.VNIC_TYPE)
        self.driver.bind_port(context)
        self._check_unbound(context)


class FPMechanismFlatTestCase(base.AgentMechanismFlatTestCase):
    def test_type_flat(self):
        context = FPPortContext(self.AGENT_TYPE,
                                self.AGENTS,
                                self.FLAT_SEGMENTS,
                                vnic_type=self.VNIC_TYPE)
        self.driver.bind_port(context)
        self._check_bound(context, self.FLAT_SEGMENTS[1])

    def test_type_flat_bad(self):
        context = FPPortContext(self.AGENT_TYPE,
                                self.AGENTS_BAD,
                                self.FLAT_SEGMENTS,
                                vnic_type=self.VNIC_TYPE)
        self.driver.bind_port(context)
        self._check_unbound(context)


class FPMechanismVlanTestCase(base.AgentMechanismVlanTestCase):
    def test_type_vlan(self):
        context = FPPortContext(self.AGENT_TYPE,
                                self.AGENTS,
                                self.VLAN_SEGMENTS,
                                vnic_type=self.VNIC_TYPE)
        self.driver.bind_port(context)
        self._check_bound(context, self.VLAN_SEGMENTS[1])

    def test_type_vlan_bad(self):
        context = FPPortContext(self.AGENT_TYPE,
                                self.AGENTS_BAD,
                                self.VLAN_SEGMENTS,
                                vnic_type=self.VNIC_TYPE)
        self.driver.bind_port(context)
        self._check_unbound(context)


class FPMechanismGreTestCase(base.AgentMechanismGreTestCase):
    def test_type_gre(self):
        context = FPPortContext(self.AGENT_TYPE,
                                self.AGENTS,
                                self.GRE_SEGMENTS)
        self.driver.bind_port(context)
        self._check_bound(context, self.GRE_SEGMENTS[1])

    def test_type_gre_bad(self):
        context = FPPortContext(self.AGENT_TYPE,
                                self.AGENTS_BAD,
                                self.GRE_SEGMENTS)
        self.driver.bind_port(context)
        self._check_unbound(context)
