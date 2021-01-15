import socket
import warnings
import sys


def is_linux():
    return sys.platform.startswith("linux")


def is_raspberrypi():
    if not is_linux():
        return False
    try:
        with open('/sys/firmware/devicetree/base/model', 'r') as m:
            return 'raspberry pi' in m.read().lower()
    except Exception:
        pass
    return False


def get_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP
