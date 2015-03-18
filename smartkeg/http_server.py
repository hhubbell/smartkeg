# ----------------------------------------------------------------------------
# Filename:     http_server.py
# Author:       Harrison Hubbell
# Date:         09/01/2014
# Description:  Is responsible for serving data over HTTP
# ----------------------------------------------------------------------------

from SocketServer import ThreadingMixIn
from smartkeg import Query
import BaseHTTPServer
import socket
import qrcode
import qrcode.image.svg
import json
import urlparse

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    _INDEX = 'index.html'    
    HTTP = {
        'OK':                   200,
        'MALFORMED':            400,
        'FILE_NOT_FOUND':       404,
        'SERVICE_UNAVAILABLE':  503
    }

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

    def get_resource(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/05/2014
        @Description:   Locates the requested resource.
        """
        page_buffer = None
        content_type = None

        if self.path[1:4] == 'api':
            if self.server.conn:
                page_buffer = self.database_transaction(self.path[5:])
                content_type = 'text/plain'
            else:
                self.send_error(self.HTTP['SERVICE_UNAVAILABLE'])

        else:
            page = self.server.root + self.INDEX if self.path[1:] == '' else self.server.root + self.path[1:]
            content_type = self.get_content_type(page)

            try:
                with open(page) as f:
                    page_buffer = f.read()
 
            except IOError:
                self.send_error(self.HTTP['FILE_NOT_FOUND'])

        return page_buffer, content_type

    def log_message(self, format, *args):
        """
        @Author:        Harrison Hubbell
        @Created:       09/01/2014
        @Description:   Overrides standard logging functionality to
                        log server actions to a file.
        """
        if self.server.logger: self.server.logger.log(('[HTTP Server]',) + args)

    def database_transaction(self, message):
        """
        @Author:        Harrison Hubbell
        @Created:       12/14/2014
        @Description:   Handle user requests that require database
                        interaction.
        """
        res = None
        parsed = urlparse.urlparse(message)
        path = parsed.path.split('/')

        if self.command == 'GET':
            params = urlparse.parse_qs(parsed.query)
        elif self.command == 'POST':
            length = int(self.headers.getheader('Content-Length'))            
            params = urlparse.parse_qs(self.rfile.read(length))

        print path, params

        if len(path) >= 2:
            if path[0] == 'get':
                if path[1] == 'beer': 
                    res = self.server.conn.SELECT(Query().get_beers(params))
                elif path[1] == 'brewer':
                    res = self.server.conn.SELECT(Query().get_brewers(params))
            elif path[0] == 'set':
                if path[1] == 'keg':
                    self.server.conn.UPDATE(Query().rem_keg(params.pop('replace', None)))
                    res = self.server.conn.INSERT(Query().set_keg(params))
                elif path[1] == 'rating':
                    res = self.server.conn.INSERT(Query().set_rating(params))
            else:
                self.send_error(self.HTTP['MALFORMED'])
        else:
            self.send_error(self.HTTP['MALFORMED'])
        
        return res

    # --------------------
    # HTTP METHODS
    # --------------------
    def do_GET(self):
        """
        @Author:        Harrison Hubbell
        @Created:       09/01/2014
        @Description:   Overrides built in GET method to handle GET requests
        """
        data, content_type = self.get_resource()

        if data and content_type:
            self.send_response(self.HTTP['OK'])
            self.send_header("Content-type", content_type)
            self.end_headers()
            self.wfile.write(data)

    def do_POST(self):
        """
        @Author:        Harrison Hubbell
        @Created:       11/21/2014
        @Description:   Overrides built in POST method to handle POST requests
        """
        data, content_type = self.get_resource()

        if data and content_type:
            self.send_response(self.HTTP['OK'])
            self.send_header("Content-type", content_type)
            self.end_headers()
            self.wfile.write(data)


class ThreadedHTTPServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):
    """Handle Requests in a Seperate Thread."""


class HTTPServer(object):
    def __init__(self, host, port, path, pipe=None, dbi=None, logger=None):
        self.httpd = ThreadedHTTPServer((host, port), RequestHandler)
        self.httpd.root = path
        self.httpd.pipe = pipe
        self.httpd.logger = logger
        self.httpd.conn = conn
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

    def serve_forever(self):
        self.httpd.serve_forever()
