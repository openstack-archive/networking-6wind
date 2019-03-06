#!/bin/bash
#
# Copyright 2019 6WIND S.A.

CONTAINER=0

# check runtime env is a container
if cat /proc/1/sched | egrep 'docker|lxc' 2>&1 > /dev/null; then
	CONTAINER=1
elif cat /proc/1/sched | head -1 | egrep 'systemd|init' 2>&1 > /dev/null; then
	CONTAINER=1
elif [ -n "$container" ]; then
	CONTAINER=1
else
	for path in "/.dockerenv" "/.dockerinit"; do  
		if [ -f "$path" ]; then 
			CONTAINER=1 
		fi 
	done
fi

if [ $CONTAINER -eq 1 ]; then
	FILE='/usr/bin/neutron-fastpath-agent-launcher.sh'
	cat << EOF > $FILE
#!/bin/bash
set -xe
sudo -u neutron /usr/bin/python2 /usr/bin/neutron-fastpath-agent --config-file /etc/neutron/rootwrap.conf --config-file /etc/neutron/neutron.conf --config-dir /etc/neutron/conf.d/common --log-file /var/log/neutron/fastpath-agent.log &
EOF
chmod +x $FILE

else
	cat << EOF > /etc/systemd/system/neutron-fastpath-agent.service
[Unit]
Description=6WIND Neutron Fast Path agent
After=virtual-accelerator.service

[Service]
User=neutron
PermissionsStartOnly=true
Type=simple
ExecStart=/usr/bin/neutron-fastpath-agent --config-file /etc/neutron/rootwrap.conf --config-file /etc/neutron/neutron.conf --config-dir /etc/neutron/conf.d/common --log-file /var/log/neutron/fastpath-agent.log
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

fi
