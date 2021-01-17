import asyncio
import io
import logging
import picamera


class StreamingOutput(object):
    """Defines output for the picamera, used by request server"""

    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = asyncio.Condition()
        self.count = 0

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
            self.count += 1
        return self.buffer.write(buf)


class Camera(object):
    def __init__(self, video_resolution, fps):
        self.logger = logging.getLogger("Camera")
        try:
            self.camera = picamera.PiCamera(resolution=video_resolution, framerate=fps)
            self.stream = StreamingOutput()
            self.camera.start_recording(self.stream, format='mjpeg')
        except Exception as e:
            self.logger.warning(e)
            self.logger.warning("Camera initialization failed, camera is not available")
            self.camera = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.camera is not None:
            self.camera.close()
