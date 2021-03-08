import logging
import os
from urllib.parse import urlparse
import paho.mqtt.client as mqtt

log = logging.getLogger(__name__)

service_name = "read-cam"


class MQTTClient(mqtt.Client):

    def __init__(self, userdata=None):

        device_name = os.environ['BALENA_DEVICE_NAME_AT_INIT']

        log.info("create mqtt client...")
        credentials = os.environ['MQTT_CREDENTIALS']
        if os.path.isfile(credentials):
            with open(credentials, 'r') as fp:
                username, pw = fp.read().split(':')
        else:
            username, pw = credentials.split(':')

        # Create client
        mqtt.Client.__init__(self, client_id="{}/{}".format(device_name, service_name), userdata=userdata)
        self.username_pw_set(username, pw)
        self.enable_logger()
        self.reconnect_delay_set(min_delay=1, max_delay=120)

        self.callbacks = {}

    def subscribe(self, topic, callback):
        self.callbacks[topic] = callback
        mqtt.Client.subscribe(self, topic)

    def on_message(self, client, userdata, msg):
        log.info("Message received-> " + msg.topic + " {}".format(msg.payload))  # Print a received msg
        for topic, callback in self.callbacks.items():
            if str(msg.topic).startswith(topic):
                callback(self, userdata, msg)

    def on_connect(self, client, userdata, flags, rc):  # The callback for when the client connects to the broker
        log.debug("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt

    def connect(self):
        mqtt_broker_address = urlparse(os.environ['MQTT_BROKER_ADDRESS'])

        log.info("connect to mqtt broker...")
        mqtt.Client.connect(self, mqtt_broker_address.hostname,
                            mqtt_broker_address.port, 60)

    def start(self):
        self.connect()
        self.loop_start()

    def stop(self):
        self.loop_stop()

