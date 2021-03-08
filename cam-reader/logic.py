from objectdb import ObjectDB
from camera import Camera
from mqtt import MQTTClient
import time
import os
import logging

log = logging.getLogger(__name__)


class AppLogic:

    def __init__(self, camera: Camera, mqtt: MQTTClient, db: ObjectDB):
        self.camera = camera
        self.mqtt = mqtt
        self.db = db

        self.device_name = os.environ['BALENA_DEVICE_NAME_AT_INIT']

        self.camera_should_be_running = False
        self.camera_should_be_recording = False

        self.mqtt.subscribe('{}/camera/1/power/toggle'.format(self.device_name), self.on_cam_toggle)
        self.mqtt.subscribe('{}/camera/1/recording/toggle'.format(self.device_name), self.on_cam_recording_toggle)

    def on_cam_toggle(self, client, userdata, msg):
        self.camera_should_be_running = bool(int(msg.payload))

    def on_cam_recording_toggle(self, client, userdata, msg):
        self.camera_should_be_recording = bool(int(msg.payload))

    def loop_forever(self):

        try:
            while True:  # send images until Ctrl-C

                if self.camera.is_on():
                    ret, image = self.camera.cap.read()
                    self.camera.add_timestamp(image)

                    if self.camera.is_recording():
                        self.camera.record(image)

                        if not self.camera_should_be_recording:
                            log.info("stop recording camera 1")
                            self.camera.stop_recording()
                            self.mqtt.publish('{}/camera/1/recording/state'.format(self.device_name), 0)
                    elif self.camera_should_be_recording:
                        log.info("start recording camera 1")
                        obj = self.db.new(suffix='.mp4', start_time=time.time(),
                            device=self.device_name, camera='camera1')
                        self.camera.start_recording(str(obj.path))
                        self.mqtt.publish('{}/camera/1/recording/state'.format(self.device_name), 1)
                    # sender.send_image(rpi_name, image)

                    if not self.camera_should_be_running:
                        log.info("stop camera 1")
                        self.camera.stop_recording()
                        self.mqtt.publish('{}/camera/1/recording/state'.format(self.device_name), 0)
                        self.camera.switch_off()
                        self.mqtt.publish('{}/camera/1/power/state'.format(self.device_name), 0)

                elif self.camera_should_be_running:
                    log.info("start camera 1")
                    self.camera.switch_on()
                    self.mqtt.publish('{}/camera/1/power/state'.format(self.device_name), 1)

                time.sleep(0.05)

        finally:
            log.info("stop things...")
            self.camera.switch_off()
