import io
import logging
import threading
import time

from PIL import Image
import cv2

from edurov_simple.hardware.camera import StreamingOutput


class RepeatingTimer(threading.Thread):
    def __init__(self, interval, function, args=None, kwargs=None):
        super().__init__()
        self.interval = interval
        self.function = function
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.finished = threading.Event()

    def cancel(self):
        """Stop the timer if it hasn't finished yet."""
        self.finished.set()

    def run(self):
        self.finished.wait(self.interval)
        while not self.finished.is_set():
            start = time.perf_counter()
            self.function(*self.args, **self.kwargs)
            self.finished.wait(self.interval - (time.perf_counter() - start))


class Camera(object):
    def __init__(self, video_resolution, fps):
        self.logger = logging.getLogger("Camera")
        self.fps = fps
        self.stream = StreamingOutput()
        self.resolution = video_resolution
        self.capture = None
        self.timer = None

    def open(self):
        try:
            self.capture = cv2.VideoCapture(0)
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            self.capture.set(cv2.CAP_PROP_SATURATION, 0.2)
            self.timer = RepeatingTimer(1 / self.fps, self.capture_frame)
            self.timer.start()
        except Exception as e:
            self.logger.warning(e)
            self.logger.warning("Camera initialization failed, camera is not available")
            self.capture = None

    def close(self):
        if self.timer is not None:
            self.timer.cancel()
            self.timer.join()
            self.timer = None
        if self.capture is not None:
            self.capture.release()
            self.capture = None

    def capture_frame(self):
        try:
            rc, img = self.capture.read()
            if not rc:
                return

            rc, buffer = cv2.imencode('.jpg', img)
            if not rc:
                return
            self.stream.write(buffer.tobytes())
        except KeyboardInterrupt:
            self.timer.cancel()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
