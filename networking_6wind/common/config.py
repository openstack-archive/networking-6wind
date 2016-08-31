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
from oslo_config import cfg
from oslo_config import types


CONF = cfg.CONF

PortType = types.Integer(1, 65535)

rpc_server_group = cfg.OptGroup(name='rpc_fp_server',
                                title='RPC FP server options')
vhostuser_group = cfg.OptGroup(name='vhostuser',
                               title='Vhostuser sockets options')
mech_driver_group = cfg.OptGroup(name='ml2_fp',
                                 title='ML2 FP plugin options')

rpc_server_opts = [
    cfg.StrOpt('bind_host',
               default='0.0.0.0',
               help='IP address to listen on.'),
    cfg.Opt('bind_port',
            type=PortType,
            default=8000,
            help='Port number to listen on.'),
]

vhostuser_opts = [
    cfg.StrOpt('socket_dir',
               default='/tmp/',
               help='Directory containing socket files'),
    cfg.StrOpt('socket_prefix',
               default='vhost-socket-',
               help='Prefix for socket filename'),
]

mech_driver_opts = [
    cfg.Opt('rpc_endpoint_port',
            type=PortType,
            default=8000,
            help='Port number to where RPC endpoint is listening.'),
    cfg.Opt('fp_info_max_age',
            type=types.Integer(1, 300),
            default=60,
            help='Age (in seconds) of valid fastpath information before new'
                 'update'),
]

CONF.register_group(rpc_server_group)
CONF.register_group(vhostuser_group)
CONF.register_group(mech_driver_group)

CONF.register_opts(rpc_server_opts, group=rpc_server_group)
CONF.register_opts(vhostuser_opts, group=vhostuser_group)
CONF.register_opts(mech_driver_opts, group=mech_driver_group)
