#!/bin/bash
#
# Copyright 2015 6WIND S.A.
#
# devstack/plugin.sh
# Functions to install/configure the fast path with ML2 ovs, linuxbridge, odl...

# Dependencies:
#
# ``functions`` file
# ``TOP_DIR`` must be defined

# ``stack.sh`` calls the entry points in this order:
# install_fast_path
# write_fast_path_conf
# start_fast_path
# setup_develop networking-6wind
# configure_nova_rootwrap
# nova_enable_monkey_patch
# configure_ml2_for_fast_path
# stop_fast_path

# Save trace setting
XTRACE=$(set +o | grep xtrace)
set +o xtrace

NET_6WIND_DIR=$DEST/networking-6wind
NOVA_ROOTWRAP=$(get_rootwrap_location nova)

function create_nova_rootwrap {
    # copy 6wind.filers for vif_ovsfp_plug scripts
    sudo cp $NET_6WIND_DIR/etc/nova/rootwrap.d/6wind.filters /etc/nova/rootwrap.d/.

    # fast-path commands are install in /usr/local, so nova-rootwrap needs to
    # be allowed to find the tools installed in /usr/local/bin.
    iniset /etc/nova/rootwrap.conf DEFAULT exec_dirs \
        "$(iniget /etc/nova/rootwrap.conf DEFAULT exec_dirs),/usr/local/bin"
}

function configure_ml2_for_fast_path {
    if [[ "$Q_DISABLE_SECURITY" == "True" ]]; then
        # disable firewall in nova
        LIBVIRT_FIREWALL_DRIVER=nova.virt.firewall.NoopFirewallDriver
        iniset $NOVA_CONF DEFAULT firewall_driver $LIBVIRT_FIREWALL_DRIVER
        inicomment $NOVA_CONF DEFAULT security_group_api
        # disable firewall in neutron
        iniset /$Q_PLUGIN_CONF_FILE securitygroup enable_security_group False
        iniset /$Q_PLUGIN_CONF_FILE securitygroup firewall_driver neutron.agent.firewall.NoopFirewallDriver
    elif [[ "$Q_USE_SECGROUP" == "True" ]]; then
        iniset /$Q_PLUGIN_CONF_FILE securitygroup enable_ipset False
        iniset $NEUTRON_CONF agent comment_iptables_rules False
    fi

    if [[ "$Q_AGENT" == "linuxbridge" ]]; then
        AGENT_BINARY=neutron-lb-fp-agent
    fi
}

function nova_set_hugepages_flavor {
    for flavor_id in $(nova flavor-list | awk '{print $2}' | grep [0-9]); do
        nova flavor-key $flavor_id set hw:mem_page_size=large
    done
}

function nova_enable_monkey_patch {
    iniset $NOVA_CONF DEFAULT monkey_patch True
    iniset $NOVA_CONF DEFAULT monkey_patch_modules \
        nova.virt.libvirt.vif:networking_6wind.monkey_patch.vif.decorator
}

# main loop
if is_service_enabled net-6wind; then
    source $NET_6WIND_DIR/devstack/libs/fast-path

    if [[ "$1" == "stack" && "$2" == "install" ]]; then
        if [[ "$OFFLINE" != "True" ]]; then
            install_fast_path
        fi
        write_fast_path_conf
        start_fast_path
        setup_develop $DEST/networking-6wind
    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        if is_service_enabled nova; then
            create_nova_rootwrap
            nova_enable_monkey_patch
        fi
        if is_service_enabled neutron; then
            configure_ml2_for_fast_path
        fi
    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        if is_service_enabled nova; then
            nova_set_hugepages_flavor
        fi
    fi

    if [[ "$1" == "unstack" ]]; then
        stop_fast_path
    fi

    if [[ "$1" == "clean" ]]; then
        uninstall_fast_path
    fi
fi

# Restore xtrace
$XTRACE
