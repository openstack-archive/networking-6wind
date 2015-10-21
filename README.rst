======================================================
networking-6wind - Neutron support for fast path stack
======================================================

ML2 Mechanism Drivers for 6WIND DPDK fast path.

Fast path technology is a user-space stack for high performance packets
offloading the Linux networking functions: IPv4/IPv6 routing, linux bridge, OVS,
iptables, conntrack...

Fast path is deployed on the compute nodes to offload the packet
processing. It can be configured with standard linux commands (i.e. iproute2,
ovs-vsctl, ...), which allow to support Neutron Mechanism Driver/Agents based on
Linux bridge or openvswitch.

* Free software: Apache license
* Documentation: http://docs.openstack.org/developer/networking-6wind
* Source: http://git.openstack.org/cgit/openstack/networking-6wind
* Bugs: http://bugs.launchpad.net/networking-6wind
