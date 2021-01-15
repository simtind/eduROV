"""
Sever classes used in the web method
"""

import socketserver
import time
from http import server
from pathlib import Path

from ..utility import get_host_ip, warning


class RequestHandler(server.BaseHTTPRequestHandler):
    """Request server, handles request from the browser"""
    base_folder = None
    index_file = None

    def do_GET(self):
        if self.path == '/':
            self.redirect('/index.html', redir_type=301)
        elif self.path.startswith('/http') or self.path.startswith('/www'):
            self.redirect(self.path[1:])
        else:
            path = self.base_folder / self.path[1:]
            if path.is_file():
                self.serve_path(str(path))
            else:
                warning(message=f'Bad response. {self.requestline}. Could not find {path}', filter='default')
                self.send_404()

    def do_POST(self):
        self.send_404()

    def serve_content(self, content, content_type='text/html'):
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', len(content))
        self.end_headers()
        self.wfile.write(content)

    def serve_path(self, path):
        if '.css' in path:
            content_type = 'text/css'
        elif '.js' in path:
            content_type = 'text/javascript'
        else:
            content_type = 'text/html'
        with open(path, 'rb') as f:
            content = f.read()
        self.serve_content(content, content_type)

    def redirect(self, path, redir_type=302):
        self.send_response(redir_type)
        self.send_header('Location', path)
        self.end_headers()

    def send_404(self):
        self.send_error(404)
        self.end_headers()

    def log_message(self, format, *args):
        return


class WebpageServer(socketserver.ThreadingMixIn, server.HTTPServer):
    """Threaded HTTP server, forwards request to the RequestHandlerClass"""
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, server_address, index_file=Path(__file__).parent / "web" / "index.html", debug=False):
        self.start = time.time()
        self.debug = debug
        RequestHandler.base_folder = Path(index_file).parent.absolute()
        RequestHandler.index_file = Path(index_file)
        super(WebpageServer, self).__init__(server_address, RequestHandler)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('Shutting down http server')
        if self.debug:
            finish = time.time()
            print(f'HTTP server was live for {finish - self.start:.1f} seconds')

