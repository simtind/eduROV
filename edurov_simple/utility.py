import socket
import warnings


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


def warning(message, filter='error', category=UserWarning):
    warnings.simplefilter(filter, category)
    warnings.formatwarning = warning_format
    warnings.warn(message)


def warning_format(message, category, filename, lineno,
                   file=None, line=None):
    return 'WARNING:\n  {}: {}\n  File: {}:{}\n'.format(
        category.__name__, message, filename, lineno)
