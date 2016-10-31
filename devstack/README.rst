====================
Enabling in Devstack
====================

1. Download DevStack::

      git clone https://git.openstack.org/openstack-dev/devstack
      cd devstack

2. Contact support@6wind.com to get Virtual Accelerator binary evaluation.
   And copy this ones into /opt/stack/fp-delivery/software

3. Add this repo as an external repository::

      > cat local.conf
      [[local|localrc]]
      enable_plugin networking-6wind http://git.openstack.org/openstack/networking-6wind

4. Enable 6WIND neutron plugin and mechanism drivers (ovs-fp/lb-fp) in local.conf::

      enable_service net-6wind
      Q_ML2_PLUGIN_MECHANISM_DRIVERS=ovs-fp

5. Enable 6WIND neutron fastpath agent in local.conf::

      enable_service net-6wind-agt

6. Run ``stack.sh``.
