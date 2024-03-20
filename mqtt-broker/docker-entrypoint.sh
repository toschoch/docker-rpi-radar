#!/bin/ash
set -e


# Expand variables in config file
configfile="${CONFIG_FILE}"
echo "expand variables in $configfile..."
./expand_vars.sh "$configfile"
echo "config is now:"
cat "$configfile"

# Set permissions
user="$(id -u)"
if [ "$user" = '0' ]; then
	[ -d "/mosquitto" ] && chown -R mosquitto:mosquitto /mosquitto || true
fi

exec "$@"