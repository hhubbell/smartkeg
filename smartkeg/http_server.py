# ----------------------------------------------------------------------------
# Filename:     http_server.py
# Author:       Harrison Hubbell
# Date:         09/01/2014
# Description:  Is responsible for serving data over HTTP
# ----------------------------------------------------------------------------

from socketserver import ThreadingMixIn
from multiprocessing import Process, Value
from ctypes import c_wchar_p
from .query import Query
import http.server
import io
import socket
import qrcode
import qrcode.image.svg
import json
import urllib.parse
import gzip
import time

class RequestHandler(http.server.BaseHTTPRequestHandler):
    _INDEX = 'index.html'    
    HTTP = {
        'OK':                   200,
        'MALFORMED':            400,
        'FORBIDDEN':            403,
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
                page_buffer = self.database_transaction(self.path[5:]).encode('utf-8')
                content_type = 'text/plain'
            else:
                self.send_error(self.HTTP['SERVICE_UNAVAILABLE'])

        elif self.path[1:4] == 'sse':
            page_buffer = self.server.sse_response.value.encode('utf-8')
            content_type = 'text/event-stream'

        else:
            page = self.server.root + self._INDEX if self.path[1:] == '' else self.server.root + self.path[1:]
            content_type = self.get_content_type(page)

            try:
                with open(page, 'rb') as f: page_buffer = f.read()
            except IOError:
                self.send_error(self.HTTP['FILE_NOT_FOUND'])

        return page_buffer, content_type

    def encode(self, stream):
        """
        @Author:        Harrison Hubbell
        @Created:       04/06/2015
        @Description:   Compresses response body.
        """
        ENCODE_AS = 'gzip'
        output = io.BytesIO()
        encoding = None
        fbuffer = stream

        if ENCODE_AS in self.headers['Accept-Encoding']:
            with gzip.GzipFile(fileobj=output, mode='w', compresslevel=5) as f:
                f.write(stream)
            
            encoding = ENCODE_AS
            fbuffer = output.getvalue()              

        return fbuffer, encoding

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
                        interaction.  get's should be method agnostic,
                        while set's should require a POST.
        """
        res = None
        parsed = urllib.parse.urlparse(message)
        path = parsed.path.split('/')

        if self.command == 'GET':
            params = urllib.parse.parse_qs(parsed.query)
        elif self.command == 'POST':
            length = int(self.headers.getheader('Content-Length'))
            params = urllib.parse.parse_qs(self.rfile.read(length))

        if len(path) >= 2:
            if path[0] == 'get':
                if path[1] == 'beer': 
                    res = json.dumps(self.server.conn.SELECT(*Query().get_beers(params)))

                elif path[1] == 'brewer':
                    res = json.dumps(self.server.conn.SELECT(*Query().get_brewers(params)))

                elif path[1] == 'serving':
                    res = json.dumps(self.server.conn.SELECT(*Query().get_now_serving()))

                elif path[1] == 'daily':
                    res = json.dumps(self.server.conn.SELECT(*Query().get_daily()))

                elif path[1] == 'remaining':
                    fmt = params.pop('format', None)
                    
                    if fmt[0] == 'percent':
                        res = json.dumps(self.server.conn.SELECT(*Query().get_percent_remaining()))

                    elif fmt[0] == 'volume':
                        res = json.dumps(self.server.conn.SELECT(*Query().get_volume_remaining()))

                    else:
                        self.send_error(self.HTTP['MALFORMED'])
                        
            elif path[0] == 'set' and self.command == 'POST':
                if path[1] == 'keg':
                    if 'replace' in params:
                        self.server.conn.UPDATE(*Query().rem_keg(params['replace']))
                        
                    res = self.server.conn.INSERT(*Query().set_keg(params))
                elif path[1] == 'rating':
                    res = self.server.conn.INSERT(*Query().set_rating(params))
                else:
                    self.send_error(self.HTTP['MALFORMED'])
            else:
                self.send_error(self.HTTP['FORBIDDEN'])
        else:
            self.send_error(self.HTTP['MALFORMED'])

        return res

    def do_GET(self):
        """
        @Author:        Harrison Hubbell
        @Created:       09/01/2014
        @Description:   Handles GET requests
        """
        data, content_type = self.get_resource()
        data, content_encoding = self.encode(data)        

        if data and content_type:
            self.send_response(self.HTTP['OK'])
            self.send_header("Content-type", content_type)
            if content_encoding:
                self.send_header("Content-encoding", content_encoding)
            self.end_headers()
            self.wfile.write(data)

    def do_POST(self):
        """
        @Author:        Harrison Hubbell
        @Created:       11/21/2014
        @Description:   Handles POST requests
        """
        data, content_type = self.get_resource()
        data, content_encoding = self.encode(data)                

        if data and content_type:
            self.send_response(self.HTTP['OK'])
            self.send_header("Content-type", content_type)
            if content_encoding:
                self.send_header("Content-encoding", content_encoding)
            self.end_headers()
            self.wfile.write(data)


class ThreadedHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    """Handle Requests in a Seperate Thread."""


class HTTPServer(object):
    def __init__(self, host, port, path, pipe=None, dbi=None, logger=None):
        self.httpd = ThreadedHTTPServer((host, port), RequestHandler)
        self.httpd.root = path
        self.httpd.pipe = pipe
        self.httpd.logger = logger
        self.httpd.conn = dbi
        self.sse = Value(c_wchar_p, '')
        self.update_id = 0
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

    def set_sse_response(self, data):
        """
        @Author:        Harrison Hubbell
        @Created:       04/06/2015
        @Description:   Manages setting the HTTPServer sse reponse.
        """
        self.update_id += 1
        self.sse.value = 'id: {}\ndata: {}\n\n'.format(self.update_id, data)

    def spawn_server(self, sse):
        """
        @Author:        Harrison Hubbell
        @Created:       04/13/2015
        @Description:   Spawn the http server instance.
        """
        self.httpd.sse_response = self.sse
        self.httpd.serve_forever()

    def serve_forever(self):
        """
        @Author:        Harrison Hubbell
        @Created:       04/13/2015
        @Description:   Spawn a thread and a shared memory pool for
                        setting new SSE responses.
        """
        Process(target=self.spawn_server, args=(self.sse,)).start()

        while True:
            if self.pipe.poll():
                self.set_sse_response(self.pipe.recv())

            time.sleep(0.1)
