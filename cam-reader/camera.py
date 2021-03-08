import cv2
import datetime
import logging

font = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (10, 400)
fontScale = 0.75
fontColor = (255, 255, 255)
lineType = 2

log = logging.getLogger(__name__)

class Camera:
    codec = cv2.VideoWriter_fourcc(*'mp4v')

    def __init__(self, camera_id: int = 0):
        self.cap = None
        self.camera_id = camera_id
        self.name = "camera{}".format(camera_id)

        self.recorder = None

    @staticmethod
    def add_timestamp(image, t=None):
        if t is None:
            t = datetime.datetime.utcnow()
        cv2.putText(image, t.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    bottomLeftCornerOfText,
                    font,
                    fontScale,
                    fontColor,
                    lineType)

    def is_on(self):
        return self.cap is not None

    def is_recording(self):
        return self.recorder is not None

    def get_resolution(self):
        width = self.cap.get(3)
        height = self.cap.get(4)
        return width, height

    def switch_on(self):
        if self.cap is not None:
            return True

        self.cap = cv2.VideoCapture(self.camera_id)

        ret, frame = self.cap.read()
        if not ret:
            self.switch_off()

        return ret

    def switch_off(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def set_resolution(self, width: int, height: int):
        self.cap.set(3, width)
        self.cap.set(4, height)

    def record(self, frame):
        self.recorder.write(frame)

    def start_recording(self, filename):
        if self.recorder is None:
            log.debug("started recording to file {}".format(filename))
            self.recorder = cv2.VideoWriter(filename, self.codec, 10,
                                            tuple(map(int, self.get_resolution())))

    def stop_recording(self):
        if self.recorder is not None:
            log.debug("stopped recording...")
            self.recorder.release()
            self.recorder = None
