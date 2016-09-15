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

# constants for the 'vif_type' field
VIF_TYPE_VHOSTUSER = 'vhostuser'

# Constants for vhostuser related fields in 'vif_details'.
# Sets mode on vhostuser socket, valid values are 'client'
# and 'server'
VIF_VHOSTUSER_MODE = 'vhostuser_mode'
# vhostuser socket path
VIF_VHOSTUSER_SOCKET = 'vhostuser_socket'
# vhostuser ovs type
VIF_VHOSTUSER_OVS_TYPE = 'vhostuser_ovs_type'
# vhostuser tap fp plug
VIF_VHOSTUSER_TAP_FP_PLUG = 'vhostuser_tap_fp_plug'
# vhostuser fp plug type
VIF_VHOSTUSER_FP_PLUG_TYPE = 'vhostuser_fp_plug_type'

# prefix for vhostuser socket name
VIF_VHOSTUSER_SOCKET_PREFIX = 'vhost-socket-'
VIF_VHOSTUSER_SOCKET_DIR = '/tmp'

# AGENT_TYPE
AGENT_TYPE_LINUXBRIDGE_FP = 'Linux bridge fast path agent'
