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

import datetime
import os

from neutron.agent import rpc as agent_rpc
from neutron_lib import constants as n_constants
from neutron.common import topics
from neutron import manager
from neutron import context

from oslo_config import cfg
from oslo_log import log as logging
from oslo_service import loopingcall

from pkg_resources import parse_version as V

cfg.CONF.import_group('vhostuser', 'networking_6wind.common.config')

LOG = logging.getLogger(__name__)


class NeutronFastPathAgent(manager.Manager):

    def __init__(self, host, conf=None):
        self.conf = conf or cfg.CONF

        self.fp_info = {
            'timestamp': '',
            'product': 'unknown',
            'product_version': 'unknown',
            'fp_active': False,
            'vhostuser_socket_dir': self.conf.vhostuser.socket_dir,
            'vhostuser_socket_prefix': self.conf.vhostuser.socket_prefix,
            'vhostuser_socket_mode': self.conf.vhostuser.mode,
            'supported_plugs': [],
        }
        self.agent_state = {
            'binary': 'neutron-fastpath-agent',
            'host': cfg.CONF.host,
            'topic': n_constants.L2_AGENT_TOPIC,
            'configurations': self.fp_info,
            'start_flag': True,
            'agent_type': 'fastpath-agent',
        }
        self.ctx = context.get_admin_context_without_session()
        self._setup_rpc()

    def init_host(self):
        self._init_fp_info()

    def _update_fp_status(self, fp_info_dict):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fp_info_dict['timestamp'] = timestamp

        try:
            status = os.system('pidof fp-rte')
            if status == 0:
                fp_info_dict['fp_active'] = True
            else:
                fp_info_dict['fp_active'] = False
        except Exception:
            fp_info_dict['fp_active'] = False

    def _init_fp_info(self):
        with open('/usr/local/etc/6WIND_product') as f:
            self.fp_info['product'] = f.read(2048).rstrip()
        with open('/usr/local/etc/6WIND_product_version') as f:
            self.fp_info['product_version'] = f.read(2048).rstrip()

        self._update_fp_status(self.fp_info)

        fp_product_version = self.fp_info['product_version']
        if self.fp_info['product'] == 'virtual-accelerator':
            self.fp_info['supported_plugs'] = ['ovs', 'bridge']
            try:
                if V(fp_product_version) >= V('1.4.0'):
                    self.fp_info['supported_plugs'].append('tap')
            except Exception:
                pass
        elif self.fp_info['product'] == '6windgate':
            self.fp_info['supported_plugs'] = ['ovs', 'bridge']
            try:
                if V(fp_product_version) >= V('4.13.0'):
                    self.fp_info['supported_plugs'].append('tap')
            except Exception:
                pass

    def _report_state(self):
        self._update_fp_status(self.fp_info)
        try:
            agent_status = self.state_rpc.report_state(self.ctx,
                                                       self.agent_state,
                                                       True)
            self.agent_state.pop('start_flag', None)
        except AttributeError:
            # This means the server does not support report_state
            LOG.warning("Neutron server does not support state report. "
                        "State report for this agent will be disabled.")
            self.heartbeat.stop()
            return
        except Exception:
            LOG.exception(_LE("Failed reporting state!"))

    def get_fp_info(self):
        # check if fp is running and fill agent configurations
        fp_info_copy = self.agent_state['configurations'].copy
        self._update_fp_status(fp_info_copy)
        return fp_info_copy

    def _setup_rpc(self):
        self.topic = "FP_AGENT"
        self.state_rpc = agent_rpc.PluginReportStateAPI(topics.REPORTS)
        # RPC network init
        # Handle updates from service
        self.endpoints = [self]
        # Define the listening consumers for the agent
        consumers = [["info", "update"]]
        self.connection = agent_rpc.create_consumers(self.endpoints,
                                                     self.topic,
                                                     consumers,
                                                     start_listening=False)

        report_interval = 30
        if report_interval:
            self.heartbeat = loopingcall.FixedIntervalLoopingCall(
                self._report_state)
            self.heartbeat.start(interval=report_interval)
