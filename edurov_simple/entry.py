import argparse

from edurov_simple.utility import get_host_ip
from edurov_simple.server.cameraserver import CameraServer
from edurov_simple.server.ioserver import IOServer
from edurov_simple.server.webserver import WebpageServer


def edurov_web():
    parser = argparse.ArgumentParser(
        description='Start the Engage eduROV web server')
    parser.add_argument(
        '-r',
        metavar='RESOLUTION',
        type=str,
        default='1024x768',
        help='''resolution, use format WIDTHxHEIGHT (default 1024x768)''')
    parser.add_argument(
        '-fps',
        metavar='FRAMERATE',
        type=int,
        default=30,
        help='framerate for the camera (default 30)')
    parser.add_argument(
        '-port',
        metavar='SERVER_PORT',
        type=int,
        default=80,
        help="which port the server should serve it's main page (default 80)")
    parser.add_argument(
        '-serial',
        metavar='SERIAL_PORT',
        type=str,
        default='/dev/ttyACM0',
        help="which serial port the script should try to use to communicate with the Arduino module")
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='set to print debug information')

    args = parser.parse_args()

    CameraServer(video_resolution=args.r, fps=args.fps, debug=args.debug)
    IOServer(args.serial, debug=args.debug)

    with WebpageServer(server_address=('', args.port), debug=args.debug) as s:
        print(f'Visit the webpage at {get_host_ip()}:{args.port}')
        s.serve_forever()


if __name__ == '__main__':
    edurov_web()
