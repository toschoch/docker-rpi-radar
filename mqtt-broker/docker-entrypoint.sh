#!/bin/ash
set -e


# Expand variables in config file
./expand_vars.sh /mosquitto.conf

# Set permissions
user="$(id -u)"
if [ "$user" = '0' ]; then
	[ -d "/mosquitto" ] && chown -R mosquitto:mosquitto /mosquitto || true
fi

exec "$@"