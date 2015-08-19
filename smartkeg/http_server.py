#
# Filename:     http_server.py
# Author:       Harrison Hubbell
# Date:         09/01/2014
# Description:  Is responsible for serving data over HTTP
#

from socketserver import ThreadingMixIn
from multiprocessing import Process, Lock
from .query import Query
import logging
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
            try:
                page_buffer, content_type = self.server.api.handle(self.command, self.path[5:], self.headers)
            except APINotConnectedError as e:
                self.send_error(503)
                logging.error(e)
            except APIMalformedError as e:
                self.send_error(400)
                logging.info(e)
            except APIForbiddenError as e:
                self.send_error(403)
                logging.info(e)

        elif self.path[1:4] == 'sse':
            page_buffer, content_type = self.server.sse.handle()

        else:
            page = self.path[1:] or self._INDEX
            content_type = self.get_content_type(page)

            try:
                with open(self.server.root + page, 'rb') as f:
                    page_buffer = f.read()
            except IOError as e: 
                self.send_error(404)
                logging.info(e)

        return page_buffer, content_type

    def encode(self, stream):
        """
        @Author:        Harrison Hubbell
        @Created:       04/06/2015
        @Description:   Compresses response body.
        """
        ENCODING = 'gzip'
        output = io.BytesIO()
        encoding = None
        fbuffer = stream

        if ENCODING in self.headers['Accept-Encoding'] and stream is not None:
            with gzip.GzipFile(fileobj=output, mode='w', compresslevel=5) as f:
                f.write(stream)
            
            encoding = ENCODING
            fbuffer = output.getvalue()              

        return fbuffer, encoding

    def log_message(self, format, *args):
        """
        @Author:        Harrison Hubbell
        @Created:       09/01/2014
        @Description:   Overrides standard logging functionality to
                        log server actions to a file.
        """
        logging.debug(args)

    def do_GET(self):
        """
        @Author:        Harrison Hubbell
        @Created:       09/01/2014
        @Description:   Handles GET requests
        """
        data, content_type = self.get_resource()
        data, content_encoding = self.encode(data)        

        if data is not None and content_type is not None:
            self.send_response(200)
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

        if data is not None and content_type is not None:
            self.send_response(200)
            self.send_header("Content-type", content_type)
            if content_encoding:
                self.send_header("Content-encoding", content_encoding)
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_error(500)
            logging.critical('{} {} caused an Internal Server Error'.format(self.command, self.path))


class SSEHandler(object):
    CONTENT_TYPE = 'text/event-stream'
    
    def __init__(self, path, lock):
        self.path = path + '/static/sse.txt'
        self.lock = lock

    def __str__(self):
        self.lock.aquire()

        with open(self.path, 'r') as f:
            data = f.read()

        self.lock.release()

        return data

    def __bytes__(self):
        self.lock.acquire()

        with open(self.path, 'rb') as f:
            data = f.read()

        self.lock.release()

        return data

    def handle(self, byte=True):
        return bytes(self) if byte else str(self), self.CONTENT_TYPE


class APIHandler(object):
    CONTENT_TYPE = 'text/plain'

    def __init__(self, dbi):
        self.dbi = dbi

    def check(self):
        if not self.dbi:
            raise APINotConnectedError

    def handle(self, method, url, headers):
        self.check()
        page_buffer = self.transact(method, url, headers).encode('utf-8')
        
        return page_buffer, self.CONTENT_TYPE

    def transact(self, method, url, headers):
        """
        @Author:        Harrison Hubbell
        @Created:       12/14/2014
        @Description:   Handle user requests that require database
                        interaction.  get's should be method agnostic,
                        while set's should require a POST.
        """
        res = None
        parsed = urllib.parse.urlparse(url)
        path = parsed.path.split('/')

        if method == 'GET':
            params = urllib.parse.parse_qs(parsed.query)
        elif method == 'POST':
            length = int(headers.getheader('Content-Length'))
            params = urllib.parse.parse_qs(self.rfile.read(length))

        if len(path) >= 2:
            if path[0] == 'get':
                if path[1] == 'beer': 
                    res = json.dumps(self.dbi.SELECT(*Query().get_beers(params)))

                elif path[1] == 'brewer':
                    res = json.dumps(self.dbi.SELECT(*Query().get_brewers(params)))

                elif path[1] == 'serving':
                    res = json.dumps(self.dbi.SELECT(*Query().get_now_serving()))

                elif path[1] == 'daily':
                    res = json.dumps(self.dbi.SELECT(*Query().get_daily()))

                elif path[1] == 'remaining':
                    fmt = params.pop('format', 'percent')
                    
                    if fmt[0] == 'percent':
                        res = json.dumps(self.dbi.SELECT(*Query().get_percent_remaining()))

                    elif fmt[0] == 'volume':
                        res = json.dumps(self.dbi.SELECT(*Query().get_volume_remaining()))
                else:
                    raise APIMalformedError(method, url)
                        
            elif path[0] == 'set' and method == 'POST':
                if path[1] == 'keg':
                    if 'replace' in params:
                        self.dbi.UPDATE(*Query().rem_keg(params['replace']))
                        
                    res = self.dbi.INSERT(*Query().set_keg(params))
                elif path[1] == 'rating':
                    res = self.dbi.INSERT(*Query().set_rating(params))
                else:
                    raise APIMalformedError(method, url)
            else:
                raise APIForbiddenError(method, url)
        else:
            raise APIMalformedError(method, url)

        return res


class APINotConnectedError(Exception):
    def __str__(self):
        return 'API has no database connection'


class APIMalformedError(Exception):
    ERRORSTRING = 'API Query "{} {}" is malformed'
    def __init__(self, method, url):
        self.method = method
        self.url = url

    def __str__(self):
        return self.ERRORSTRING.format(self.method, self.url)


class APIForbiddenError(APIMalformedError):
    ERRORSTRING = 'API Query "{} {}" is forbidden'

    
class ThreadedHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    """Handle Requests in a Seperate Thread."""
    def __init__(self, addr, handler, api, sse, root):
        super(ThreadedHTTPServer, self).__init__(addr, handler)
        self.api = api
        self.sse = sse
        self.root = root


class HTTPServerManager(object):
    def __init__(self, host, port, path, dbi=None):
        self.host = host
        self.port = port
        self.path = path
        self.dbi = dbi
        self.update_id = 0
        self.lock = Lock();        
        self.create_qrcode()

    def create_qrcode(self):
        """
        @Author:        Harrison Hubbell
        @Created:       11/18/2014
        @Description:   Gets the current interface address of the server,
                        and renders a QR Code that allows devices to go 
                        to that address.
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
        image.save(self.path + 'static/img/qrcode.svg')

    def sse_response(self, data):
        """
        @Author:        Harrison Hubbell
        @Created:       04/06/2015
        @Description:   Manages setting the HTTPServer sse reponse.
        """
        self.lock.acquire()
        
        with open(self.path + '/static/sse.txt', 'w') as f:
            self.update_id += 1
            f.write('id: {}\ndata: {}\n\n'.format(self.update_id, data))
            
        self.lock.release()
            
    def spawn_server(self, host=None, port=None):
        """
        @Author:        Harrison Hubbell
        @Created:       04/13/2015
        @Description:   Spawn the http server instance.
        """
        host = host if host is not None else self.host
        port = port if port is not None else self.port
        
        self.httpd = ThreadedHTTPServer(
            (host, port),
            RequestHandler,
            APIHandler(self.dbi),
            SSEHandler(self.path, self.lock),
            self.path
        )
        
        self.httpd.serve_forever()

    def start(self):
        """
        @Author:        Harrison Hubbell
        @Created:       04/13/2015
        @Description:   Spawn a thread and a shared memory pool for
                        setting new SSE responses.
        """
        Process(target=self.spawn_server).start()
