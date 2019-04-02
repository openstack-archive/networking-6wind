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

from neutron_lib import constants
from oslo_config import cfg


CONF = cfg.CONF

mech_driver_group = cfg.OptGroup(name='ovs_fp',
                                 title='ovs-fp ML2 plugin options')

mech_driver_opts = [
    cfg.BoolOpt('ovs_agent_required', default=True,
                help=_("Set to false to enable driver to complete port "
                       "binding without presence of "
                       "neutron-openvswitch-agent")),
    cfg.ListOpt('allowed_network_types', default=[constants.TYPE_VLAN,
                                                  constants.TYPE_VXLAN,
                                                  constants.TYPE_GRE],
                help=_("List of network segment types for which "
                       "driver is allowed to complete port binding. "
                       "Ignored if ovs_agent_required"))
]

CONF.register_group(mech_driver_group)
CONF.register_opts(mech_driver_opts, group=mech_driver_group)
