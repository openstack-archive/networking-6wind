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
# stop_fast_path

# Save trace setting
XTRACE=$(set +o | grep xtrace)
set +o xtrace

NET_6WIND_DIR=$DEST/networking-6wind
NOVA_ROOTWRAP=$(get_rootwrap_location nova)

# main loop
if is_service_enabled net-6wind; then
    source $NET_6WIND_DIR/devstack/libs/fast-path

    if [[ "$1" == "stack" && "$2" == "install" ]]; then
        if [[ "$OFFLINE" != "True" ]]; then
            install_fast_path
        fi
        write_fast_path_conf
        start_fast_path
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
