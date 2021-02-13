import zmq
import pyarrow as pa
from zmqarrow import ZmqArrow
import os
import time
from processings import RDMProcessor
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

n_fft_range = 384
n_fft_doppler = 256


log.info("RDM processing with range fft {} and doppler fft {}".format(n_fft_range, n_fft_doppler))
zmq_input = os.environ.get("ZMQ_INPUT", "localhost:5555")
input_address = "tcp://{}".format(zmq_input)
log.info("Listen on {}".format(input_address))
port = os.environ.get("ZMQ_PORT", "5556")
log.info("Result is served on port {}".format(port))

processor = RDMProcessor(n_fft_range, n_fft_doppler)

log_every_n_second = 120
t_last_log = time.time()
frames_processed = 0

log.info("start processing...")
with ZmqArrow(address=input_address) as sub:
    with ZmqArrow(address="tcp://*:{}".format(port), socket_type=zmq.PUB) as pub:
        while True:
            t, tensor = sub.zmq_socket.recv_time_and_tensor(copy=False)
            amp, phases = processor.process_fft(tensor.to_numpy())
            pub.zmq_socket.send_time_and_tensor(t, pa.Tensor.from_numpy(amp), copy=False)

            frames_processed += 1
            t = time.time()
            if frames_processed == 1 or ((t - t_last_log) > log_every_n_second):
                log.info("{} frames processed".format(frames_processed))
                t_last_log = t

