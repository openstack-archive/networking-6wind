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

from networking_6wind._i18n import _LE
from networking_6wind.common import constants
from networking_6wind.common import utils

from neutron.agent import rpc as agent_rpc
from neutron import manager

from neutron_lib.agent import topics
from neutron_lib import constants as n_constants
from neutron_lib import context

from oslo_config import cfg
from oslo_log import log as logging
from oslo_service import loopingcall

from pkg_resources import parse_version as V


LOG = logging.getLogger(__name__)

CFG_PATH = "/etc"
PRODUCT_FILE = "6WIND_product"
PRODUCT_VERSION_FILE = "6WIND_product_version"


class NeutronFastPathAgent(manager.Manager):

    def __init__(self, host, conf=None):
        try:
            sock_dir, sock_mode = utils.get_socket_settings()
        except Exception:
            sock_dir = constants.VHOSTUSER_SOCKET_DIR
            sock_mode = constants.VHOSTUSER_SOCKET_MODE
            LOG.warning("Cannot get vhostuser socket info from fp-vdev, use "
                        "default path '%s' and mode '%s'" % (sock_dir,
                                                             sock_mode))
        self.fp_info = {
            'timestamp': '',
            'product': 'unknown',
            'product_version': 'unknown',
            'active': False,
            'vhostuser_socket_dir': sock_dir,
            'vhostuser_socket_prefix': constants.VHOSTUSER_SOCKET_PREFIX,
            'vhostuser_socket_mode': sock_mode,
            'supported_plugs': [],
        }
        self.agent_state = {
            'binary': 'neutron-fastpath-agent',
            'host': cfg.CONF.host,
            'topic': n_constants.L2_AGENT_TOPIC,
            'configurations': self.fp_info,
            'start_flag': True,
            'agent_type': constants.FP_AGENT_TYPE,
        }
        self.ctx = context.get_admin_context_without_session()
        self._setup_rpc()
        self.init_host()

    def init_host(self):
        self._init_fp_info()

    def _update_fp_status(self, fp_info_dict):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fp_info_dict['timestamp'] = timestamp

        try:
            status = os.system('pidof fp-rte > /dev/null 2>&1')
            if status == 0:
                fp_info_dict['active'] = True
            else:
                fp_info_dict['active'] = False
        except Exception:
            fp_info_dict['active'] = False

    def _init_fp_info(self):
        with open(os.path.join(CFG_PATH, PRODUCT_FILE)) as f:
            self.fp_info['product'] = f.read(2048).rstrip()
        with open(os.path.join(CFG_PATH, PRODUCT_VERSION_FILE)) as f:
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
            self.state_rpc.report_state(self.ctx, self.agent_state, True)
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
        fp_info_copy = self.agent_state['configurations'].copy()
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
