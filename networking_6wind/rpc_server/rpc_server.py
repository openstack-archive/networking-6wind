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
import os

import datetime

from oslo_config import cfg

from pkg_resources import parse_version as V

import SimpleXMLRPCServer

cfg.CONF.import_group('rpc_fp_server', 'networking_6wind.common.config')
cfg.CONF.import_group('vhostuser', 'networking_6wind.common.config')


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


class RpcFPServer(object):
    def __init__(self):
        self.conf_rpc = cfg.CONF.rpc_fp_server
        self.conf_vhostuser = cfg.CONF.vhostuser

        self.server = SimpleXMLRPCServer.SimpleXMLRPCServer(
            (self.conf_rpc.bind_host,
             self.conf_rpc.bind_port),
            requestHandler=RequestHandler)
        self.fp_info = {
            'timestamp': '',
            'product': 'unknown',
            'product_version': 'unknown',
            'active': False,
            'vhostuser_socket_dir': self.conf_vhostuser.socket_dir,
            'vhostuser_socket_prefix': self.conf_vhostuser.socket_prefix,
            'vhostuser_socket_mode': 'client',
            'supported_plugs': ['ovs', 'bridge'],
        }

    def run(self):
        self.server.register_introspection_functions()
        self.server.register_function(self.get_fp_info)

        # Run the server's main loop
        self.server.serve_forever()

    def get_fp_info(self):
        fp_info_copy = self.fp_info.copy()

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fp_info_copy['timestamp'] = timestamp

        try:
            with open('/usr/local/etc/6WIND_product') as f:
                fp_info_copy['product'] = f.read(2048).rstrip()
            with open('/usr/local/etc/6WIND_product_version') as f:
                fp_info_copy['product_version'] = f.read(2048).rstrip()
        except IOError:
            fp_info_copy['product'] = ''
            fp_info_copy['product_version'] = ''

        try:
            status = os.system('pidof fp-rte')
            if status == 0:
                fp_info_copy['active'] = True
            else:
                fp_info_copy['active'] = False
        except Exception:
            fp_info_copy['active'] = False

        fp_product_version = fp_info_copy['product_version']
        if fp_info_copy['product'] == 'virtual-accelerator':
            try:
                if V(fp_product_version) >= V('1.4.0'):
                    fp_info_copy['supported_plugs'].append('tap')
            except Exception:
                pass
        elif fp_info_copy['product'] == '6windgate':
            try:
                if V(fp_product_version) >= V('4.13.0'):
                    fp_info_copy['supported_plugs'].append('tap')
            except Exception:
                pass

        return fp_info_copy


def main():
    # Create server
    rpc_fp_server = RpcFPServer()
    # Launch server
    rpc_fp_server.run()
