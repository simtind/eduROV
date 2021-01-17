import asyncio
import io
import logging
from PIL import Image
import cv2


class StreamingOutput(object):
    """Defines output for the picamera, used by request server"""

    def __init__(self):
        self.frame = None
        self._new_frame = False
        self.buffer = io.BytesIO()
        self.condition = asyncio.Condition()
        self.count = 0

    async def notify_if_new(self):
        if self._new_frame:
            self.condition.notify_all()
            self._new_frame = False

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            self.frame = self.buffer.getvalue()
            self._new_frame = True
            self.buffer.seek(0)
            self.count += 1
        return self.buffer.write(buf)


class Camera(object):
    def __init__(self, video_resolution, fps):
        self.logger = logging.getLogger("Camera")
        self.fps = fps
        try:
            self.capture = cv2.VideoCapture(0)
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, video_resolution[0])
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, video_resolution[1])
            self.capture.set(cv2.CAP_PROP_SATURATION, 0.2)

            self.stream = StreamingOutput()

            self.task = asyncio.get_event_loop().create_task(self.capture_frame())
        except Exception as e:
            self.logger.warning(e)
            self.logger.warning("Camera initialization failed, camera is not available")
            self.camera = None

    def close(self):
        self.task.cancel()
        if self.camera is not None:
            self.camera.close()

    async def capture_frame(self):
        while True:
            try:
                sleep = asyncio.create_task(asyncio.sleep(1 / self.fps))
                rc, img = self.capture.read()
                if not rc:
                    continue
                imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                jpg = Image.fromarray(imgRGB)
                async with self.stream.condition:
                    jpg.save(self.stream, 'JPEG')
                    await self.stream.notify_if_new()
                await sleep
            except KeyboardInterrupt:
                break

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
