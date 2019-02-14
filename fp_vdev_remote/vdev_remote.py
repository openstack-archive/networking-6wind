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

import argparse
import httplib
import socket
import sys
import xmlrpclib

sockfile = "/run/openvswitch/fp-rpcd.sock"


class UnixStreamHTTPConnection(httplib.HTTPConnection):
    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.host)


class UnixStreamTransport(xmlrpclib.Transport, object):
    def __init__(self, socket_path):
        self.socket_path = socket_path
        super(UnixStreamTransport, self).__init__()

    def make_connection(self, host):
        return UnixStreamHTTPConnection(self.socket_path)


def main():
    parser = argparse.ArgumentParser(prog="fp-vdev-remote",
                                     description='Run fp-vdev utilities on '
                                     'remote through XMLRPC')
    _, unknown_args = parser.parse_known_args()

    args = ' '.join(unknown_args)

    # Set the first argument to 'http://' to let xmlrpclib.Server happy.
    # Not needed in our case as we use a UNIX socket as transport
    s = xmlrpclib.Server('http://', transport=UnixStreamTransport(sockfile))

    ret, out, err = s.fp_vdev_cmd(args)
    sys.stderr.write(err)
    sys.stdout.write(out)
    return ret
