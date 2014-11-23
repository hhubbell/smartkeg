# ----------------------------------------------------------------------------
# Filename:     http_server.py
# Author:       Harrison Hubbell
# Date:         09/01/2014
# Description:  Is responsible for serving data over HTTP
# ----------------------------------------------------------------------------

from ConfigParser import ConfigParser
from SocketServer import ThreadingMixIn
from process import ChildProcess
from logger import SmartkegLogger
import BaseHTTPServer
import socket
import qrcode
import qrcode.image.svg
import json
import urlparse

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    HTTP_OK  = 200
    HTTP_MALFORMED = 400
    HTTP_FILE_NOT_FOUND = 404
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
            page = self.server.root + self._INDEX
        else:
            page = self.server.root + self.path[1:]

        return page

    def log_message(self, format, *args):
        """
        @Author:        Harrison Hubbell
        @Created:       09/01/2014
        @Description:   Overrides standard logging functionality to
                        log server actions to a file.
        """
        if self.server.logger: self.server.logger.log(('[HTTP Server]',) + args)

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

    def do_POST(self):
        """
        @Author:        Harrison Hubbell
        @Created:       11/21/2014
        @Description:   Overrides built in POST method to handle POST
                        requests, primarily from form submissions.
        """
        length = int(self.headers.getheader('Content-Length'))
        form_data = urlparse.parse_qs(self.rfile.read(length))
        req_type = form_data.pop('action', None)[0]

        if req_type == 'get' or req_type == 'set':
            self.server.pipe.send({
                'type': req_type,
                'data': form_data.pop('data', None)[0],
                'params': form_data
            })

            response = self.server.pipe.recv()
            self.send_response(self.HTTP_OK)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(response)
            
        else:
            self.send_error(self.HTTP_MALFORMED)


class HTTPServer(BaseHTTPServer.HTTPServer):
    def set_connection(self, pipe):
        """
        @Author:        Harrison Hubbell
        @Created:       11/21/2014
        @Description:   Sets process connection
        """
        self.pipe = pipe

    def set_logger(self, logger):
        """
        @Author:        Harrison Hubbell
        @Created:       11/21/2014
        @Description:   Sets logger object of server.
        """
        self.logger = logger

    def set_root_directory(self, directory):
        """
        @Author:        Harrison Hubbell
        @Created:       11/21/2014
        @Description:   Sets the directory to serve files from.
        """
        self.root = directory


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle Requests in a Seperate Thread."""


class SmartkegHTTPServer(ChildProcess):
    def __init__(self, pipe, host, port, directory, logger=None):
        super(SmartkegHTTPServer, self).__init__(pipe)    
        self.httpd = ThreadedHTTPServer((host, port), RequestHandler)
        self.httpd.set_root_directory(directory)
        self.httpd.set_connection(pipe)
        self.httpd.set_logger(logger)
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
        image.save(self.httpd.root + 'static/img/qrcode.svg')

    def main(self):
        self.httpd.serve_forever()
