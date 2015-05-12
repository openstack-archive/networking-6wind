#!/usr/bin/python

#    Copyright 2015 6WIND S.A.
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

from __future__ import print_function

import argparse
import os
import sys

from oslo_concurrency import processutils

from nova.utils import execute

from networking_6wind.plug_scripts import utils
from networking_6wind.plug_scripts import vhostuser


# -----------------------------------------------------------------------------
def get_br_name(iface_id):
    return ('qbr' + iface_id)[:utils.NIC_NAME_LEN]


def get_veth_pair_names(iface_id):
    return (('qvb%s' % iface_id)[:utils.NIC_NAME_LEN],
            ('qvo%s' % iface_id)[:utils.NIC_NAME_LEN])


def is_hybrid_plug(vif):
    if vif['port_filter'].lower() == 'true':
        return True
    if vif['ovs_hybrid_plug'].lower() == 'true':
        return True
    return False


# -----------------------------------------------------------------------------
def plug_ovs_bridge(vif):
    iface_id = vif['ovs_interfaceid']
    dev = vif['devname']
    try:
        utils.plug_ovs_vif_port(vif['bridge_name'],
                                dev, iface_id, vif['address'],
                                vif['instance_id'])
    except processutils.ProcessExecutionError as exception:
        utils.log_exception("Failed to plug ovs", exception)


def plug_ovs_hybrid(vif):
    iface_id = vif['ovs_interfaceid']
    br_name = get_br_name(vif['id'])
    v1_name, v2_name = get_veth_pair_names(vif['id'])
    dev = vif['devname']
    try:
        if not utils.device_exists(br_name):
            execute('brctl', 'addbr', br_name, run_as_root=True)
            execute('brctl', 'setfd', br_name, 0, run_as_root=True)
            execute('brctl', 'stp', br_name, 'off', run_as_root=True)
            execute('tee', '/sys/class/net/%s/bridge/multicast_snooping'
                    % br_name, process_input='0',
                    run_as_root=True, check_exit_code=[0, 1])

        if not utils.is_device_on_bridge(dev):
            execute('brctl', 'addif', br_name, dev, run_as_root=True)

        if not utils.device_exists(v2_name):
            utils.create_veth_pair(v1_name, v2_name)
            execute('ip', 'link', 'set', br_name, 'up', run_as_root=True)
            execute('brctl', 'addif', br_name, v1_name, run_as_root=True)
            utils.plug_ovs_vif_port(vif['bridge_name'], v2_name, iface_id,
                                    vif['address'], vif['instance_id'])
    except processutils.ProcessExecutionError as exception:
        utils.log_exception("Failed to plug ovs (hybrid)", exception)


def plug_ovs(vif):
    # get a vhostuser port
    try:
        vhostuser_port = vhostuser.get_vhostuser_port(vif['devname'],
                                                      vif['vhostuser_socket'])
    except processutils.ProcessExecutionError as exception:
        utils.log_exception("Failed to get a new vhostuser port", exception)
        sys.exit(1)

    if vhostuser_port is None:
        nb_devices = vhostuser.count_vhostuser_ports()
        print("Not enough vhostuser ports availables (max devices=%d)",
              nb_devices)
        sys.exit(1)

    if not is_hybrid_plug(vif):
        plug_ovs_bridge(vif)
    else:
        plug_ovs_hybrid(vif)


def unplug_ovs_bridge(vif):
    try:
        utils.unplug_ovs_vif_port(vif['bridge_name'], vif['devname'])
    except processutils.ProcessExecutionError as exception:
        utils.log_exception("Failed to unplug ovs", exception)


def unplug_ovs_hybrid(vif):
    br_name = get_br_name(vif['id'])
    v1_name, v2_name = get_veth_pair_names(vif['id'])
    dev = vif['devname']
    try:
        if utils.device_exists(br_name):
            execute('brctl', 'delif', br_name, v1_name, run_as_root=True)
            execute('brctl', 'delif', br_name, dev, run_as_root=True)
            execute('ip', 'link', 'set', br_name, 'down', run_as_root=True)
            execute('brctl', 'delbr', br_name, run_as_root=True)

        utils.unplug_ovs_vif_port(vif['bridge_name'], v2_name)
        utils.delete_net_dev(v2_name)
    except processutils.ProcessExecutionError as exception:
        utils.log_exception("Failed to unplug ovs (hybrid)", exception)


def unplug_ovs(vif):
    if not is_hybrid_plug(vif):
        unplug_ovs_bridge(vif)
    else:
        unplug_ovs_hybrid(vif)

    try:
        vhostuser.put_vhostuser_port(vif['devname'])
    except processutils.ProcessExecutionError as exception:
        utils.log_exception("Failed to free vhostuser port", exception)


# -----------------------------------------------------------------------------
# main
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', metavar='ACTION',
                        help='Action to perform with vif on the ovs bridge',
                        choices=['plug', 'unplug'])
    args = parser.parse_args()

    args.vif = {}

    # mandatory environnement variable
    args.vif['id'] = os.getenv('VIF_ID')
    args.vif['address'] = os.getenv('VIF_ADDRESS')
    args.vif['instance_id'] = os.getenv('VIF_INSTANCE_ID')
    args.vif['vhostuser_socket'] = os.getenv('VIF_DETAILS_VHOSTUSER_SOCKET')

    if args.vif['id'] is None:
        parser.error('missing VIF_ID environment variable')
    if args.vif['address'] is None:
        parser.error('missing VIF_ADDRESS environment variable')
    if args.vif['instance_id'] is None:
        parser.error('missing VIF_INSTANCE_ID environment variable')
    if args.vif['vhostuser_socket'] is None:
        parser.error('missing VIF_DETAILS_VHOSTUSER_SOCKET'
                     ' environment variable')

    # optionnal environnement variable
    default_devname = "tap" + args.vif['id'][:utils.NIC_NAME_LEN]
    args.vif['devname'] = os.getenv('VIF_DEVNAME', default_devname)
    args.vif['ovs_interfaceid'] = os.getenv('VIF_OVS_INTERFACEID',
                                            args.vif['id'])
    # TOFIX: bridge_name should be given by VIF_NETWORK_BRIDGE
    args.vif['bridge_name'] = 'br-int'
    args.vif['port_filter'] = os.getenv('VIF_DETAILS_PORTS_FILTER', 'false')
    args.vif['ovs_hybrid_plug'] = os.getenv('VIF_DETAILS_OVS_HYBRID_PLUG',
                                            'false')

    return args


def main():
    args = parse_args()

    if args.action == 'plug':
        plug_ovs(args.vif)
    else:
        unplug_ovs(args.vif)
