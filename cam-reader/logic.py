import logging
import os
import time

import imagezmq

from camera import Camera
from mqtt import MQTTClient
from storageapi.client import Client

log = logging.getLogger(__name__)


class AppLogic:

    def __init__(self, camera: Camera, mqtt: MQTTClient, storage: Client, streamer: imagezmq.ImageSender):
        self.camera = camera
        self.mqtt = mqtt
        self.storage = storage
        self.streamer = streamer

        self.device_name = os.environ['BALENA_DEVICE_NAME_AT_INIT']

        self.camera_should_be_running = False
        self.camera_should_be_recording = False
        self.record = None

        self.target_fps = 10

        self.frame_counter = 0
        self.t_start_counter = 0
        self.t_start_frame = 0
        self.effective_fps = self.target_fps
        self.proc_time = 0.05
        self.sleep_s = 1. / self.target_fps - self.proc_time

        self.mqtt.subscribe('{}/camera/{}/power/toggle'.format(self.device_name, self.camera.camera_id),
                            self.on_cam_toggle)
        self.mqtt.subscribe('{}/camera/{}/recording/toggle'.format(self.device_name, self.camera.camera_id),
                            self.on_cam_recording_toggle)
        self.camera_state_topic = '{}/camera/{}/power/state'.format(self.device_name, self.camera.camera_id)
        self.recording_state_topic = '{}/camera/{}/recording/state'.format(self.device_name, self.camera.camera_id)
        self.camera_fps_topic = '{}/camera/{}/fps'.format(self.device_name, self.camera.camera_id)

    def on_cam_toggle(self, client, userdata, msg):
        self.camera_should_be_running = bool(int(msg.payload))

    def on_cam_recording_toggle(self, client, userdata, msg):
        self.camera_should_be_recording = bool(int(msg.payload))

    def start_cam(self):
        log.info("start {} on {}...".format(self.camera.name, self.device_name))
        self.camera.switch_on()
        self.mqtt.publish_timed_value(self.camera_state_topic, 1)

    def stop_cam(self):
        log.info("stop {} on {}...".format(self.camera.name, self.device_name))
        self.camera.stop_recording()
        self.mqtt.publish_timed_value(self.recording_state_topic, 0)
        self.camera.switch_off()
        self.mqtt.publish_timed_value(self.camera_state_topic, 0)

    def start_recording(self):
        log.info("start recording on {} ({})...".format(self.camera.name, self.device_name))
        if not self.camera.is_on():
            self.start_cam()

        self.camera.set_recording_fps(self.target_fps)
        self.record = self.storage.create(bucket='videos', date=time.time(), meta=self.camera.meta)

        self.camera.start_recording(str(self.record.location))
        self.mqtt.publish_timed_value(self.recording_state_topic, 1)

    def stop_recording(self):
        log.info("stop recording on {} ({})...".format(self.camera.name, self.device_name))
        self.camera.stop_recording()
        self.mqtt.publish_timed_value(self.recording_state_topic, 0)
        if self.record is not None:
            self.record.meta['end_time'] = time.time()
            self.storage.finalize(self.record)

    def start_frame(self):
        self.t_start_frame = time.time()

    def end_proc(self):
        self.proc_time = time.time() - self.t_start_frame
        self.sleep_s = max(1. / self.target_fps - self.proc_time, 0)

    def count_frame_rate(self, reset=False):

        if reset or self.frame_counter % (5 * 60 * self.target_fps) == 0:
            log.info("avg. frame rate is {} fps".format(self.effective_fps))
            self.mqtt.publish_timed_value(self.camera_fps_topic, self.effective_fps)
            self.t_start_counter = time.time()
            self.frame_counter = 0

        self.frame_counter = self.frame_counter + 1

        if self.frame_counter % (30 * self.target_fps) == 0:
            self.effective_fps = self.frame_counter / (time.time() - self.t_start_counter)

    def loop_forever(self):

        try:
            if self.camera.is_on():
                self.mqtt.publish_timed_value(self.camera_state_topic, 1)
            else:
                self.mqtt.publish_timed_value(self.camera_state_topic, 1)

            while True:  # send images until Ctrl-C
                self.start_frame()
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
                self.count_frame_rate()
                self.end_proc()
                time.sleep(self.sleep_s)

        finally:
            log.info("stop things...")
            self.camera.switch_off()
