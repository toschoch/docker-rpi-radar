import socket
import time
import imagezmq
import cv2
import os
import sys

# Accept connections on all tcp addresses, port xxxx
port = os.environ.get("ZMQ_PORT", "5553")
sender = imagezmq.ImageSender(connect_to="tcp://*:{}".format(port), REQ_REP=False)

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
