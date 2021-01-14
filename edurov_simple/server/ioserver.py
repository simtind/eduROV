import json
import multiprocessing
import asyncio
import websockets as websockets

from edurov_simple.hardware.arduino import Arduino
from edurov_simple.hardware.sensehat import SystemMonitor


class IOServer(multiprocessing.Process):
    """ Creates a new process that Exposes the ROV sensors and actuators as a websocket data stream """
    def __init__(self, arduino_serial_port, arduino_baud_rate=115200, port=8081):
        self.port = port
        self.serial_port = arduino_serial_port
        self.baud_rate = arduino_baud_rate
        self.sensors = dict()
        self.condition = asyncio.Condition()
        super().__init__(target=self._runner, daemon=True)
        self.start()

    async def _collect_arduino_sensors(self, arduino):
        while True:
            await asyncio.sleep(1)
            with self.condition:
                self.sensors.update(await arduino.get_sensors())
                self.condition.notify_all()

    async def _collect_system_sensors(self):
        raspberry = SystemMonitor()
        while True:
            await asyncio.sleep(10)
            with self.condition:
                self.sensors.update(await raspberry.get_sensors())
                self.condition.notify_all()

    async def _send_sensors(self, websocket, arduino):
        arduino = self._collect_arduino_sensors(arduino)
        system = self._collect_system_sensors()

        while True:
            await self.condition
            with self.condition:
                await websocket.send(self.sensors)

    async def _receive_input(self, websocket, arduino):
        while True:
            data = await websocket.receive()
            arduino.set_actuators(json.loads(data))

    async def _handler(self, websocket, path):
        arduino = Arduino(self.serial_port, self.baud_rate)
        sensors = self._send_sensors(websocket, arduino)
        input = self._receive_input(websocket, arduino)

        asyncio.get_event_loop().run_forever()

    def _runner(self):
        with websockets.serve(self._handler, "localhost", self.port) as server:
            asyncio.get_event_loop().run_until_complete(server)
            asyncio.get_event_loop().run_forever()
