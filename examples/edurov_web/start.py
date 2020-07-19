import os
import time

import Pyro4

from edurov import WebMethod
from edurov.utils import detect_pi, serial_connection, send_arduino, \
    receive_arduino, free_drive_space, cpu_temperature

if detect_pi():
    from sense_hat import SenseHat


def valid_arduino_string(arduino_string):
    if arduino_string:
        if arduino_string.count(':') == 2:
            try:
                [float(v) for v in arduino_string.split(':')]
                return True
            except:
                return False
    return False


def arduino():
    ser = serial_connection()
    with Pyro4.Proxy("PYRONAME:ROVSyncer") as rov:
        while rov.run:

            data = {
                'vertical':   int(rov.actuators["vertical"] * 100),
                'starboard':  int(rov.actuators["starboard"] * 100),
                'port':       int(rov.actuators["port"] * 100),
                'lights':     int(rov.actuators['lights'])
            }
            message = "vertical={vertical};starboard={starboard};port={port};lights={lights}".format(**data)
            if ser:
                send_arduino(msg=message, serial_connection=ser)
            else:
                print(message)
            if ser:
                arduino_string = receive_arduino(serial_connection=ser)
                if valid_arduino_string(arduino_string):
                    v1, v2, v3 = arduino_string.split(':')
                    rov.sensor = {
                        'tempWater': float(v1),
                        'pressureWater': float(v2),
                        'batteryVoltage': float(v3)
                    }


def senser():
    sense = SenseHat()
    with Pyro4.Proxy("PYRONAME:ROVSyncer") as rov:
        while rov.run:
            orientation = sense.get_orientation()
            rov.sensor = {'temp': sense.get_temperature(),
                          'pressure': sense.get_pressure() / 10,
                          'humidity': sense.get_humidity(),
                          'pitch': orientation['pitch'],
                          'roll': orientation['roll'] + 180,
                          'yaw': orientation['yaw']}


def system_monitor():
    with Pyro4.Proxy("PYRONAME:ROVSyncer") as rov:
        while rov.run:
            rov.sensor = {'free_space': free_drive_space(),
                          'cpu_temp': cpu_temperature()}
            time.sleep(10)


def main(video_resolution='1024x768', fps=30, server_port=8000, debug=False):
    web_method = WebMethod(
        index_file=os.path.join(os.path.dirname(__file__), 'index.html'),
        video_resolution=video_resolution,
        fps=fps,
        server_port=server_port,
        debug=debug,
        runtime_functions=[arduino, senser, system_monitor]
    )
    web_method.serve()


if __name__ == '__main__':
    main()
