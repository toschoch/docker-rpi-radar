from camera import Camera
import logging
import imagezmq
import cv2
import os
from mqtt import MQTTClient

if os.path.isfile('.env'):
    from dotenv import load_dotenv

    load_dotenv()



logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

mqtt = MQTTClient()


# Accept connections on all tcp addresses, port xxxx
port = os.environ.get("ZMQ_PORT", "5553")
sender = imagezmq.ImageSender(connect_to="tcp://*:{}".format(port), REQ_REP=False)

rpi_name = "RadarPiCam"  # send RPi hostname with each image


camera = Camera()


state_requested = True


def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
    status = bool(int(msg.payload))
    log.info("Message received-> " + msg.topic + " {}".format(status))  # Print a received msg
    global state_requested
    if status and not camera.is_on():
        state_requested = True
    if not status and camera.is_on():
        state_requested = False

mqtt.client.on_message = on_message

camera.switch_on()
mqtt.start()

try:
    while True:  # send images until Ctrl-C

        if camera.is_on():
            ret, image = camera.cap.read()
            camera.add_timestamp(image)

            camera.record(image)
            sender.send_image(rpi_name, image)
            if not state_requested:
                camera.stop_recording()
                camera.switch_off()
        elif state_requested:
            camera.switch_on()
            camera.start_recording()

        key = cv2.waitKey(100)

        if key == ord('q'):
            raise Exception()

finally:
    print("stop things...")
    camera.switch_off()
