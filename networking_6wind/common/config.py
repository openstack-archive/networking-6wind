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


CONF = cfg.CONF

vhostuser_group = cfg.OptGroup(name='vhostuser',
                               title='Vhostuser sockets options')
vhostuser_opts = [
    cfg.StrOpt('socket_dir',
               default='/tmp/',
               help='Directory containing socket files'),
    cfg.StrOpt('socket_prefix',
               default='vhost-socket-',
               help='Prefix for socket filename'),
    cfg.StrOpt('mode',
               default='client',
               help='Socket mode'),
]

CONF.register_group(vhostuser_group)
CONF.register_opts(vhostuser_opts, group=vhostuser_group)
