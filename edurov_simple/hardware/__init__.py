def is_raspberrypi():
    import sys
    if not sys.platform.startswith("linux"):
        return False
    try:
        with open('/sys/firmware/devicetree/base/model', 'r') as m:
            return 'raspberry pi' in m.read().lower()
    except Exception:
        pass
    return False


# Import mock interfaces if not running on raspberry pi.
if not is_raspberrypi():
    from .mock import system as system
    from .mock import arduino as arduino
else:
    from . import system as system
    from . import arduino as arduino
