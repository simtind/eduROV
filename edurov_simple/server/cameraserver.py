import io
import logging
import multiprocessing
import asyncio
import subprocess
import time

import websockets as websockets

from edurov_simple.hardware import is_raspberrypi
from edurov_simple.utility import get_host_ip

if is_raspberrypi():
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


class CameraServer(multiprocessing.Process):
    """ Creates a new process that Exposes the raspberry pi camera as a websocket image stream """
    def __init__(self, video_resolution='1024x768', fps=30, port=8080):
        self.logger = logging.getLogger("CameraServer")
        self.port = port
        self.video_resolution = video_resolution.split('x')
        self.fps = fps
        self.start_time = time.time()

        if is_raspberrypi():
            camera = subprocess.check_output(['vcgencmd', 'get_camera']).decode().rstrip()
            if '0' in camera:
                raise RuntimeError('Camera not enabled or connected properly')

            super().__init__(target=self._runner, daemon=True)
            self.start()
        else:
            self.logger.debug("No mock module available for camera, skipping")

    async def _handler(self, websocket, path):
        while True:
            await self.camera_stream.condition
            await websocket.send(self.camera_stream.frame)

    def _runner(self):
        with picamera.PiCamera(resolution=self.video_resolution, framerate=self.fps) as camera:
            self.camera_stream = StreamingOutput()
            camera.start_recording(self.camera_stream, format='mjpeg')

            server = websockets.serve(self._handler, "localhost", self.port)
            self.logger.info(f"Camera websocket server started at {get_host_ip()}:{self.port}")
            asyncio.get_event_loop().run_until_complete(server)
            asyncio.get_event_loop().run_forever()

        self.logger.info('Shutting down camera server')
        finish = time.time()
        seconds = finish - self.start_time
        framerate = self.camera_stream.count / (finish - self.start_time)
        self.logger.debug(f'Sent {self.camera_stream.count} images in {seconds:.1f} seconds at {framerate:.2f} fps')

