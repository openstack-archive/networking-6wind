====================
Enabling in Devstack
====================

1. Download DevStack::

      git clone https://git.openstack.org/openstack-dev/devstack
      cd devstack

2. Contact support@6wind.com to get Virtual Accelerator binary evaluation.
   And copy this ones into /opt/stack/fp-delivery

3. Add this repo as an external repository::

      > cat local.conf
      [[local|localrc]]
      enable_plugin networking-6wind http://git.openstack.org/openstack/networking-6wind
      enable_service net-6wind

4. Run ``stack.sh``.
