from objectdb import ObjectDB
from camera import Camera
from mqtt import MQTTClient
import imagezmq
import time
import os
import logging

log = logging.getLogger(__name__)


class AppLogic:

    def __init__(self, camera: Camera, mqtt: MQTTClient, db: ObjectDB, streamer: imagezmq.ImageSender):
        self.camera = camera
        self.mqtt = mqtt
        self.db = db
        self.streamer = streamer

        self.device_name = os.environ['BALENA_DEVICE_NAME_AT_INIT']

        self.camera_should_be_running = False
        self.camera_should_be_recording = False
        self.record = None

        self.mqtt.subscribe('{}/camera/1/power/toggle'.format(self.device_name), self.on_cam_toggle)
        self.mqtt.subscribe('{}/camera/1/recording/toggle'.format(self.device_name), self.on_cam_recording_toggle)

    def on_cam_toggle(self, client, userdata, msg):
        self.camera_should_be_running = bool(int(msg.payload))

    def on_cam_recording_toggle(self, client, userdata, msg):
        self.camera_should_be_recording = bool(int(msg.payload))

    def start_cam(self):
        log.info("start camera 1")
        self.camera.switch_on()
        self.mqtt.publish('{}/camera/1/power/state'.format(self.device_name), 1)

    def stop_cam(self):
        log.info("stop camera 1")
        self.camera.stop_recording()
        self.mqtt.publish('{}/camera/1/recording/state'.format(self.device_name), 0)
        self.camera.switch_off()
        self.mqtt.publish('{}/camera/1/power/state'.format(self.device_name), 0)

    def start_recording(self):
        log.info("start recording camera 1")
        self.record = self.db.new(suffix='.mp4', start_time=time.time(),
                          device=self.device_name, camera='camera1')
        self.camera.start_recording(str(self.record.path))
        self.mqtt.publish('{}/camera/1/recording/state'.format(self.device_name), 1)

    def stop_recording(self):
        log.info("stop recording camera 1")
        self.camera.stop_recording()
        self.mqtt.publish('{}/camera/1/recording/state'.format(self.device_name), 0)
        if self.record is not None:
            self.db.created(self.record)

    def loop_forever(self):

        try:
            while True:  # send images until Ctrl-C

                if self.camera.is_on():
                    ret, image = self.camera.cap.read()
                    self.camera.add_timestamp(image)
                    self.streamer.send_image(self.device_name, image)

                    if self.camera.is_recording():
                        self.camera.record(image)

                        if not self.camera_should_be_recording:
                            self.stop_recording()

                    elif self.camera_should_be_recording:
                        self.start_recording()

                    if not self.camera_should_be_running:
                        self.stop_cam()

                elif self.camera_should_be_running:
                    self.start_cam()

                time.sleep(0.05)

        finally:
            log.info("stop things...")
            self.camera.switch_off()
