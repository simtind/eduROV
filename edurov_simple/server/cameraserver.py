import io
import multiprocessing
import asyncio
import websockets as websockets

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
        self.port = port
        self.video_resolution = video_resolution.split('x')
        self.fps = fps
        super().__init__(target=self._runner, daemon=True)
        self.start()

    async def _handler(self, websocket, path):
        while True:
            await self.camera_stream.condition
            await websocket.send(self.camera_stream.frame)

    def _runner(self):
        with picamera.PiCamera(resolution=self.video_resolution, framerate=self.fps) as camera:
            self.camera_stream = StreamingOutput()
            camera.start_recording(self.camera_stream, format='mjpeg')

            with websockets.serve(self._handler, "localhost", self.port) as server:
                asyncio.get_event_loop().run_until_complete(server)
                asyncio.get_event_loop().run_forever()

