# Copyright 2016 6WIND SA
#
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

import sys

from oslo_config import cfg
from oslo_service import service

from neutron.agent.common import config
from neutron.common import config as common_config
from neutron import service as neutron_service


def main():
    common_config.init(sys.argv[1:])
    config.setup_logging()
    server = neutron_service.Service.create(
        binary='neutron-fastpath-agent',
        topic="FP_AGENT",
        report_interval=30,
        manager='networking_6wind.agent.server.NeutronFastPathAgent')
    service.launch(cfg.CONF, server).wait()
