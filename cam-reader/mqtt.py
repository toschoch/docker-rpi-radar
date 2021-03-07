import logging
import os
from urllib.parse import urlparse
import paho.mqtt.client as mqtt

log = logging.getLogger(__name__)

service_name = "read-cam"


class MQTTClient:

    def __init__(self):

        device_name = os.environ['BALENA_DEVICE_NAME_AT_INIT']

        log.info("create mqtt client...")
        credentials = os.environ['MQTT_CREDENTIALS']
        if os.path.isfile(credentials):
            with open(credentials, 'r') as fp:
                username, pw = fp.read().split(':')
        else:
            username, pw = credentials.split(':')

        # Create client
        client = mqtt.Client(client_id="{}/{}".format(device_name, service_name), userdata=self)
        client.username_pw_set(username, pw)
        client.enable_logger()
        client.reconnect_delay_set(min_delay=1, max_delay=120)

        self.client = client
        self.client.on_connect = self._on_connect
        self.subscribe_to = ['{}/cameras/cam1/start'.format(device_name)]

    @staticmethod
    def _on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
        log.debug("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
        userdata.on_connect()

    def on_connect(self):
        for topic in self.subscribe_to:
            self.client.subscribe(topic)

    def connect(self):
        mqtt_broker_address = urlparse(os.environ['MQTT_BROKER_ADDRESS'])

        log.info("connect to mqtt broker...")
        self.client.connect(mqtt_broker_address.hostname,
                            mqtt_broker_address.port, 60)

    def start(self):
        self.connect()
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()