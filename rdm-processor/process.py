import time
from zmqarrow import ZmqArrow
import os
from processings import RDMProcessor


port = os.environ.get("ZMQ_PORT", "5553")
processor = RDMProcessor(384, 256)

with ZmqArrow(address="tcp://*:{}".format(port)) as con:
    while True:
        t, tensor = con.zmq_socket.recv_time_and_tensor(copy=False)
        amp, phases = RDMProcessor.process_fft(tensor.to)

rpi_name = "RadarPiCam"  # send RPi hostname with each image

cap = cv2.VideoCapture(0)
ret, frame = cap.read()
if not ret:
    print('Failed to open default camera. Exiting...')
    sys.exit()
cap.set(3, 640)
cap.set(4, 480)

time.sleep(2.0)  # allow camera sensor to warm up
while True:  # send images until Ctrl-C
    ret, image = cap.read()
    sender.send_image(rpi_name, image)
    cv2.waitKey(100)
