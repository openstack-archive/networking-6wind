#    Copyright 2015 6WIND S.A.
#    All Rights Reserved.
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


# base timestamp
BASE_TIMESTAMP = '1970-01-01 00:00:00'

# linuxbridge name prefix
BRIDGE_PREFIX = 'brq'

# fp agent type
FP_AGENT_TYPE = '6WIND Fast Path agent'

# path to fp-rcpd.sock
FP_RPCD_SOCKET_PATH = '/run/openvswitch/fp-rpcd.sock'

# vhostuser socket settings
VHOSTUSER_SOCKET_DIR = '/tmp'
VHOSTUSER_SOCKET_MODE = 'client'
VHOSTUSER_SOCKET_PREFIX = 'vhost-socket-'

# vhostuser fp plug
# duplicate this constant from nova.network.model.py,
# in case of containerized setups: nova modules can be installed
# in another container than neutron ML2 plugins
VIF_DETAILS_VHOSTUSER_FP_PLUG = 'vhostuser_fp_plug'
