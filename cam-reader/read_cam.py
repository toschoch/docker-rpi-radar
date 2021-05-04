import os

if os.path.isfile('.env'):
    from dotenv import load_dotenv

    load_dotenv()

from camera import Camera
import logging
import imagezmq
from logic import AppLogic
from mqtt import MQTTClient
from storageapi.client import Client


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

mqtt = MQTTClient()

storage = Client(os.environ.get("STORAGE_API_URL"))

# Accept connections on all tcp addresses, port xxxx
port = os.environ.get("ZMQ_PORT", "5553")
sender = imagezmq.ImageSender(connect_to="tcp://*:{}".format(port), REQ_REP=False)

rpi_name = "RadarPiCam"  # send RPi hostname with each image

camera = Camera()

camera.switch_on()
mqtt.start()

logic = AppLogic(camera, mqtt, storage, sender)

logic.loop_forever()
