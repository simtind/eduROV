import json
import multiprocessing
import asyncio
import time

import websockets as websockets

from ..hardware import arduino
from ..hardware import system
from ..utility import get_host_ip


class IOServer(multiprocessing.Process):
    """ Creates a new process that Exposes the ROV sensors and actuators as a websocket data stream """
    def __init__(self, arduino_serial_port='/dev/ttyACM0', arduino_baud_rate=115200, port=8081, debug=False):
        self.port = port
        self.serial_port = arduino_serial_port
        self.baud_rate = arduino_baud_rate
        self.sensors = dict()
        self.start_time = time.time()
        self.debug = debug
        self.condition = None

        super().__init__(target=self._runner, daemon=True)
        self.start()

    async def _collect_arduino_sensors(self, arduino):
        while True:
            await asyncio.sleep(1)
            print("Get arduino data")
            async with self.condition:
                self.sensors.update(await arduino.get_sensors())
                self.condition.notify_all()

    async def _collect_system_sensors(self):
        raspberry = system.SystemMonitor()
        while True:
            print("Get system data")
            await asyncio.sleep(10)
            async with self.condition:
                self.sensors.update(await raspberry.get_sensors())
                self.condition.notify_all()

    async def _send_sensors(self, websocket):
        while True:
            print("Wait for sensor data to arrive")
            await self.condition
            async with self.condition:
                await websocket.send(json.dumps(self.sensors))

    async def _receive_input(self, websocket):
        while True:
            data = await websocket.recv()
            await self.arduino.set_actuators(json.loads(data))

    async def _handler(self, websocket, path):
        asyncio.create_task(self._send_sensors(websocket))
        asyncio.create_task(self._receive_input(websocket))
        print("Testing sockets")
        name = await websocket.recv()
        print(f"< {name}")

        greeting = f"Hello {name}!"

        await websocket.send(greeting)
        print(f"> {greeting}")

    def _runner(self):
        self.condition = asyncio.Condition()

        server = websockets.serve(self._handler, "localhost", self.port)
        print(f"I/O websocket server started at ws://{get_host_ip()}:{self.port}")

        print("Ready to send sensor data")
        self.arduino = arduino.Arduino(self.serial_port, self.baud_rate)
        asyncio.get_event_loop().create_task(self._collect_arduino_sensors(self.arduino))
        asyncio.get_event_loop().create_task(self._collect_system_sensors())

        asyncio.get_event_loop().run_until_complete(server)
        asyncio.get_event_loop().run_forever()

        print('Shutting down i/o server')
        if self.debug:
            finish = time.time()
            seconds = finish - self.start_time
            print(f'I/O server was live for {seconds:.1f} seconds')
