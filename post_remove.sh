#!/bin/bash
#
# Copyright 2019 6WIND S.A.
#

CONTAINER_LAUNCHER='/usr/bin/neutron-fastpath-agent-launcher.sh'
SERVICE='/etc/systemd/system/neutron-fastpath-agent.service'

for file in $CONTAINER_LAUNCHER $SERVICE; do
    if [ -e $file ]; then
        rm -rf $file
    fi
done
