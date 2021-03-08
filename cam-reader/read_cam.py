from camera import Camera
import logging
#import imagezmq
from logic import AppLogic
import os
from mqtt import MQTTClient
from objectdb import ObjectDB

if os.path.isfile('.env'):
    from dotenv import load_dotenv

    load_dotenv()

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

mqtt = MQTTClient()

db = ObjectDB(mqtt)

# Accept connections on all tcp addresses, port xxxx
port = os.environ.get("ZMQ_PORT", "5553")
#sender = imagezmq.ImageSender(connect_to="tcp://*:{}".format(port), REQ_REP=False)

rpi_name = "RadarPiCam"  # send RPi hostname with each image

camera = Camera(0)

camera.switch_on()
mqtt.start()

logic = AppLogic(camera, mqtt, db)

logic.loop_forever()
