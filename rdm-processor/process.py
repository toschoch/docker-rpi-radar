import json

import zmq
import pyarrow as pa
from zmqarrow import ZmqArrow
import os
import time
from processings import RDMProcessor
from buffer import Buffer
from storageapi.client import Client
from lowpass import Filter
from mqtt import MQTTClient
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

n_fft_range = 384
n_fft_doppler = 256

device_name = os.environ['BALENA_DEVICE_NAME_AT_INIT']


log.info("RDM processing with range fft {} and doppler fft {}".format(n_fft_range, n_fft_doppler))
zmq_input = os.environ.get("ZMQ_INPUT", "localhost:5555")
input_address = "tcp://{}".format(zmq_input)
log.info("Listen on {}".format(input_address))
port = os.environ.get("ZMQ_PORT", "5556")
log.info("Result is served on port {}".format(port))

mqtt = MQTTClient()

processor = RDMProcessor(n_fft_range, n_fft_doppler)
storage_api = Client(base_url=os.environ.get("STORAGE_API_URL", "https://storage-service"))
buffer = Buffer(storage_api)

mqtt.start()

log_every_n_second = 120
t_last_log = time.time()
frames_processed = 0

filter = Filter(3)
filter_bg = Filter(300)

log.info("start processing...")
with ZmqArrow(address=input_address) as sub:
    with ZmqArrow(address="tcp://*:{}".format(port), socket_type=zmq.PUB) as pub:
        while True:
            t_frame, tensor = sub.zmq_socket.recv_time_and_tensor(copy=False)
            raw = tensor.to_numpy()
            buffer.append(t_frame, raw)
            amp, phases = processor.process_fft(raw)

            img_act = filter(t_frame, amp)
            img_bg = filter_bg(t_frame, amp)
            img = ((img_act - img_bg) / (img_act + img_bg) + 0.2)

            pub.zmq_socket.send_time_and_tensor(t_frame, pa.Tensor.from_numpy(img), copy=False)

            mqtt.publish('{}/radar/activity/max'.format(device_name),
                         payload=json.dumps({'time': t_frame.isoformat(), 'value': img.max()}))

            frames_processed += 1
            t = time.time()

            if frames_processed == 1 or ((t - t_last_log) > log_every_n_second):
                log.info("{} frames processed".format(frames_processed))
                t_last_log = t

