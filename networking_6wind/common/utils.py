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

import os

from neutron.agent.linux import utils

from networking_6wind.common import constants

FP_VDEV_CMD = None
FP_VDEV_CMD_CHECK = False


def command_exists(cmd):
    return not bool(os.system('which %s > /dev/null 2>&1' % cmd))


def get_vdev_cmd():
    global FP_VDEV_CMD
    global FP_VDEV_CMD_CHECK
    if FP_VDEV_CMD_CHECK is False:
        if command_exists('fp-vdev'):
            FP_VDEV_CMD = 'fp-vdev'
        elif command_exists('fp-vdev-remote') and \
            os.path.exists(constants.FP_RPCD_SOCKET_PATH):
            FP_VDEV_CMD = 'fp-vdev-remote'
        FP_VDEV_CMD_CHECK = True
    return FP_VDEV_CMD


def get_socket_settings():
    fp_vdev_bin = FP_VDEV_CMD
    if fp_vdev_bin is None:
        fp_vdev_bin = get_vdev_cmd()
    path = utils.execute(cmd=[fp_vdev_bin, 'get', 'sockfolder'],
                         run_as_root=True)
    mode = utils.execute(cmd=[fp_vdev_bin, 'get', 'sockmode'],
                         run_as_root=True)
    return (path.strip(), mode.strip())


def get_vif_vhostuser_socket(socket_prefix, socket_dir, port_id):
    vhostuser_socket_name = socket_prefix + port_id
    return os.path.join(socket_dir, vhostuser_socket_name)
