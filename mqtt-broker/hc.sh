#!/bin/sh
# shellcheck disable=SC2016
mosquitto_sub -h dietzi.ch -t '$SYS/broker/version' -u radar-pi -P "${MQTT_SERVER_PW}" -C 1 > /dev/null 2>&1
dietzi_broker_down="$?"
# shellcheck disable=SC2016
dietzi_bridge_ok_topic="\$SYS/broker/connection/${BALENA_DEVICE_NAME_AT_INIT}-bridge/state"
dietzi_bridge_ok=$(mosquitto_sub -h 0.0.0.0 -t \'"$dietzi_bridge_ok_topic"\' -C 1 2> /dev/null)

# shellcheck disable=SC2181
if [ "$?" -ne 0 ]; then
  echo "Error: local broker not reachable"
  exit 1
fi

if [ $dietzi_broker_down -eq 0 ] && [ "$dietzi_bridge_ok" = "0" ]; then
  echo "Error: remote broker online but bridge connection is down"
  exit 1
fi

exit 0