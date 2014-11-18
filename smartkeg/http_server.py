# ----------------------------------------------------------------------------
# Filename:     http_server.py
# Author:       Harrison Hubbell
# Date:         09/01/2014
# Description:  Is responsible for serving data over HTTP
# ----------------------------------------------------------------------------

from ConfigParser import ConfigParser
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
from logger import SmartkegLogger
import socket
import qrcode
import qrcode.image.svg
import json

class RequestHandler(BaseHTTPRequestHandler):
    HTTP_OK  = 200
    HTTP_FILE_NOT_FOUND = 404
    _BASE_DIR = '/usr/local/src/smartkeg/'
    _CONFIG_PATH = _BASE_DIR + 'etc/config.cfg'
    _SERVER_DIR = _BASE_DIR + 'srv/'
    _INDEX = 'index.html'

    def get_content_type(self, req):
        """ 
        @Author:        Harrison Hubbell
        @Created:       09/01/2014
        @Description:   Return content type based on file.  Essentially
                        just a lot of if statements
        """
        if req.endswith('.css'):    return 'text/css'
        if req.endswith('.html'):   return 'text/html'
        if req.endswith('.ico'):    return 'image/x-icon'
        if req.endswith('.js'):     return 'application/javascript'
        if req.endswith('.pdf'):    return 'application/pdf'
        if req.endswith('.png'):    return 'image/png'
        if req.endswith('.svg'):    return 'image/svg+xml'

    def get_page(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/05/2014
        @Description:   Locates the requested page.
        """
        if self.path[1:] is '':
            page = self._SERVER_DIR + self._INDEX
        else:
            page = self._SERVER_DIR + self.path[1:]

        return page

    def log_message(self, format, *args):
        """
        @Author:        Harrison Hubbell
        @Created:       09/01/2014
        @Description:   Overrides standard logging functionality to
                        log server actions to a file.
        """
        logger = SmartkegLogger(self._CONFIG_PATH)
        logger.log(('[HTTP Server]',) + args)

    # --------------------
    # HTTP METHODS
    # --------------------
    def do_GET(self):
        """
        @Author:        Harrison Hubbell
        @Created:       09/01/2014
        @Description:   Overrides built in GET method to handle GET requests
        """
        page = self.get_page()
        content_type = self.get_content_type(page)

        try:
            with open(page) as p:
                self.send_response(self.HTTP_OK)
                self.send_header('Content-type', content_type)
                self.end_headers()
                self.wfile.write(p.read())
        except IOError:
            self.send_error(self.HTTP_FILE_NOT_FOUND)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle Requests in a Seperate Thread."""


class SmartkegHTTPServer:
    _BASE_DIR = '/usr/local/src/smartkeg/'
    _SERVER_DIR = _BASE_DIR + 'srv/'
    
    def __init__(self, host, port):
        self.httpd = ThreadedHTTPServer((host, port), RequestHandler)
        self.create_qrcode()

    def create_qrcode(self):
        """
        @Author:        Harrison Hubbell
        @Created:       11/18/2014
        @Description:   Gets the current interface address of the server, and
                        renders a QR Code that allows devices to go to that
                        address.
        """
        GOOGLE = ('8.8.8.8', 80)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(GOOGLE)
        address = 'http://' + sock.getsockname()[0]
        sock.close()
 
        factory = qrcode.image.svg.SvgPathImage
        factory.QR_PATH_STYLE = 'fill:#C0392B;fill-opacity:1;fill-rule:nonzero;stroke:none'

        qr = qrcode.QRCode(version=1, box_size=10, border=0)
        qr.image_factory = factory
        qr.add_data(address)
        qr.make()

        image = qr.make_image()
        image.save(self._SERVER_DIR + 'static/img/qrcode.svg')

    def main(self):
        self.httpd.serve_forever()

if __name__ == '__main__':
    _BASE_DIR = '/usr/local/src/smartkeg/'
    _CONFIG_PATH = _BASE_DIR + 'etc/config.cfg'
    _HEADER = 'SmartkegHTTPServer'

    cfg = ConfigParser()
    cfg.read(_CONFIG_PATH)
    host = cfg.get(_HEADER, 'host')
    port = cfg.getint(_HEADER, 'port')

    server = SmartkegHTTPServer(host, port)
    server.main()
